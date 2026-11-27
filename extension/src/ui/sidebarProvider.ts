import * as vscode from "vscode";
import * as crypto from "crypto";
import { ICodeOwnClient } from "../client/interface";
import { getSidebarHtml } from "./views/sidebarHtml";

export class CodeOwnSidebarProvider implements vscode.WebviewViewProvider {
  private view?: vscode.WebviewView;

  constructor(
    private readonly extensionUri: vscode.Uri,
    private clientProvider: () => ICodeOwnClient,
    private workspaceRoot: string
  ) {}

  public resolveWebviewView(
    webviewView: vscode.WebviewView,
    _context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken
  ) {
    this.view = webviewView;

    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [this.extensionUri]
    };

    this.update();

    webviewView.webview.onDidReceiveMessage(async (data) => {
      const client = this.clientProvider();
      switch (data.command) {
        case "openCheck":
          vscode.commands.executeCommand("codeown.openCheck");
          break;
        case "refresh":
          vscode.commands.executeCommand("codeown.refresh");
          break;
        case "setApiKey":
          vscode.commands.executeCommand("codeown.setApiKey");
          break;
        case "replyNudge":
          try {
            const status = await client.status();
            if (status.pending_nudge) {
              const text = await vscode.window.showInputBox({
                prompt: `Trả lời Nudge: ${status.pending_nudge.question}`,
                placeHolder: "Nhập giải thích ngắn gọn..."
              });
              if (text !== undefined) {
                await client.ackNudge(status.pending_nudge.id, "reply", text.trim());
                vscode.window.showInformationMessage("Đã gửi phản hồi Nudge.");
                this.update();
              }
            }
          } catch (e: any) {
            vscode.window.showErrorMessage(`Lỗi phản hồi Nudge: ${e.message}`);
          }
          break;
      }
    });
  }

  public async update() {
    if (!this.view) return;
    try {
      const client = this.clientProvider();
      const status = await client.status();
      const ledger = await client.ledgerList();
      const nonce = crypto.randomBytes(16).toString("hex");

      this.view.webview.html = getSidebarHtml(nonce, status, ledger.items || []);
    } catch {
      this.view.webview.html = `<!DOCTYPE html><html><body><p>Đang kết nối tới CodeOwn CLI...</p></body></html>`;
    }
  }
}
