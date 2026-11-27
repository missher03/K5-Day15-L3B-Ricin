import * as vscode from "vscode";
import { ICodeOwnClient } from "./client/interface";
import { CliCodeOwnClient } from "./client/cliClient";
import { MockCodeOwnClient } from "./client/mockClient";
import { promptSetApiKey } from "./secrets";
import { StatusBarController } from "./ui/statusBar";
import { CodeOwnSidebarProvider } from "./ui/sidebarProvider";
import { CheckPanel } from "./ui/checkPanel";

let clientInstance: ICodeOwnClient | undefined;
let statusBarController: StatusBarController | undefined;
let sidebarProvider: CodeOwnSidebarProvider | undefined;

export function activate(context: vscode.ExtensionContext) {
  const workspaceFolders = vscode.workspace.workspaceFolders;
  const workspaceRoot = workspaceFolders && workspaceFolders.length > 0 
    ? workspaceFolders[0].uri.fsPath 
    : process.cwd();

  const getClient = (): ICodeOwnClient => {
    if (!clientInstance) {
      const config = vscode.workspace.getConfiguration("codeown");
      const mockMode = config.get<boolean>("mockMode") || false;
      if (mockMode) {
        clientInstance = new MockCodeOwnClient();
      } else {
        clientInstance = new CliCodeOwnClient(context, workspaceRoot);
      }
    }
    return clientInstance;
  };

  // Reset client on config change
  context.subscriptions.push(
    vscode.workspace.onDidChangeConfiguration((e) => {
      if (e.affectsConfiguration("codeown")) {
        clientInstance = undefined;
        if (statusBarController) {
          statusBarController.poll();
        }
        if (sidebarProvider) {
          sidebarProvider.update();
        }
      }
    })
  );

  // Sidebar provider
  sidebarProvider = new CodeOwnSidebarProvider(context.extensionUri, getClient, workspaceRoot);
  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider("codeown.sidebarView", sidebarProvider)
  );

  // Status bar controller
  statusBarController = new StatusBarController(context, getClient);
  statusBarController.setOnStateUpdated(() => {
    if (sidebarProvider) {
      sidebarProvider.update();
    }
  });
  statusBarController.startPolling();

  // Register commands
  context.subscriptions.push(
    vscode.commands.registerCommand("codeown.enable", async () => {
      const actionRulesOnly = "Chỉ rules (--rules-only)";
      const actionFull = "Khởi tạo đầy đủ";
      const choice = await vscode.window.showQuickPick([actionFull, actionRulesOnly], {
        placeHolder: "Chọn chế độ khởi tạo CodeOwn cho repo này"
      });
      if (!choice) return;
      const rulesOnly = choice === actionRulesOnly;

      try {
        const client = getClient();
        const res = await client.init(rulesOnly);
        vscode.window.showInformationMessage(`CodeOwn đã được bật thành công cho ${res.repo || workspaceRoot}!`);
        statusBarController?.poll();
        sidebarProvider?.update();
      } catch (e: any) {
        vscode.window.showErrorMessage(`Lỗi khởi tạo CodeOwn: ${e.message}`);
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
      await CheckPanel.createOrShow(context.extensionUri, getClient(), workspaceRoot, () => {
        sidebarProvider?.update();
      });
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("codeown.openLedger", async () => {
      await CheckPanel.createOrShow(context.extensionUri, getClient(), workspaceRoot, () => {
        sidebarProvider?.update();
      });
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand("codeown.refresh", async () => {
      clientInstance = undefined;
      await statusBarController?.poll();
      await sidebarProvider?.update();
      vscode.window.showInformationMessage("Đã làm mới trạng thái CodeOwn.");
    })
  );
}

export function deactivate() {
  if (statusBarController) {
    statusBarController.dispose();
  }
  if (CheckPanel.currentPanel) {
    CheckPanel.currentPanel.dispose();
  }
}
