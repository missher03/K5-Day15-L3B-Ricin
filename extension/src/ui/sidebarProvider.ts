import * as crypto from "crypto";
import * as vscode from "vscode";
import { ICodeOwnClient } from "../client/interface";
import { getSidebarHtml } from "./views/sidebarHtml";

interface SidebarMsg {
  command?: string;
}

// Quan ly Sidebar CodeOwn o Activity Bar
export class CodeOwnSidebarProvider implements vscode.WebviewViewProvider {
  private view?: vscode.WebviewView;

  constructor(
    private readonly extensionUri: vscode.Uri,
    private clientProvider: () => ICodeOwnClient
  ) {}

  public resolveWebviewView(webviewView: vscode.WebviewView): void {
    this.view = webviewView;
    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [this.extensionUri]
    };

    webviewView.webview.onDidReceiveMessage((msg: SidebarMsg) => {
      if (msg.command === "openCheck") {
        void vscode.commands.executeCommand("codeown.openCheck");
      } else if (msg.command === "refresh") {
        void vscode.commands.executeCommand("codeown.refresh");
      } else if (msg.command === "setApiKey") {
        void vscode.commands.executeCommand("codeown.setApiKey");
      }
    });

    void this.update();
  }

  public async update(): Promise<void> {
    if (!this.view) {
      return;
    }
    const nonce = crypto.randomBytes(16).toString("hex");
    try {
      const client = this.clientProvider();
      const [status, ledger] = await Promise.all([
        client.status().catch(() => null),
        client.ledgerList().catch(() => ({ items: [], recent_nudges: [] }))
      ]);
      this.view.webview.html = getSidebarHtml(nonce, status, ledger.items, ledger.recent_nudges);
    } catch {
      this.view.webview.html = getSidebarHtml(nonce, null, [], []);
    }
  }
}
