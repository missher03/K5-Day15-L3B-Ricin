import * as vscode from "vscode";
import { CliCodeOwnClient } from "./client/cliClient";
import { ICodeOwnClient } from "./client/interface";
import { MockCodeOwnClient } from "./client/mockClient";
import { promptSetApiKey } from "./secrets";
import { CheckPanel } from "./ui/checkPanel";
import { CodeOwnSidebarProvider } from "./ui/sidebarProvider";
import { StatusBarController } from "./ui/statusBar";
import { formatError } from "./utils/html";

let clientInstance: ICodeOwnClient | undefined;
let statusBarController: StatusBarController | undefined;
let sidebarProvider: CodeOwnSidebarProvider | undefined;

export function activate(context: vscode.ExtensionContext): void {
  const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath ?? process.cwd();

  const getClient = (): ICodeOwnClient => {
    if (!clientInstance) {
      const mockMode = vscode.workspace.getConfiguration("codeown").get<boolean>("mockMode") ?? false;
      clientInstance = mockMode
        ? new MockCodeOwnClient()
        : new CliCodeOwnClient(context, workspaceRoot);
    }
    return clientInstance;
  };

  sidebarProvider = new CodeOwnSidebarProvider(context.extensionUri, getClient);
  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider("codeown.sidebarView", sidebarProvider)
  );

  statusBarController = new StatusBarController(context, getClient);
  statusBarController.setOnStateUpdated(() => {
    void sidebarProvider?.update();
  });
  statusBarController.startPolling();

  context.subscriptions.push(
    vscode.workspace.onDidChangeConfiguration((e) => {
      if (e.affectsConfiguration("codeown")) {
        clientInstance = undefined;
        void statusBarController?.poll();
        void sidebarProvider?.update();
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("codeown.enable", async () => {
      const modeFull = "Bật đầy đủ (gồm AI phân loại prompt)";
      const modeRules = "Chỉ dùng luật (--rules-only, không gửi prompt)";
      const choice = await vscode.window.showQuickPick([modeFull, modeRules], {
        placeHolder: "Sẽ ghi hook vào .claude/, .git/hooks/post-commit và thêm .codeown/ vào .gitignore"
      });
      if (!choice) return;

      try {
        const res = await getClient().init(workspaceRoot, choice === modeRules);
        vscode.window.showInformationMessage(
          `Đã bật CodeOwn (${res.hooks_written.length} hook).`
        );
        await statusBarController?.poll();
        await sidebarProvider?.update();
      } catch (err) {
        vscode.window.showErrorMessage(`Lỗi bật CodeOwn: ${formatError(err)}`);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("codeown.setApiKey", async () => {
      await promptSetApiKey(context);
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("codeown.openCheck", async () => {
      const taskId = statusBarController?.getLastTaskId() ?? "current";
      await CheckPanel.createOrShow(getClient(), workspaceRoot, taskId, () => {
        void sidebarProvider?.update();
      });
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("codeown.openLedger", async () => {
      await vscode.commands.executeCommand("codeown.sidebarView.focus");
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("codeown.refresh", async () => {
      clientInstance = undefined;
      await statusBarController?.poll();
      await sidebarProvider?.update();
    })
  );
}

export function deactivate(): void {
  statusBarController?.dispose();
  CheckPanel.currentPanel?.dispose();
}
