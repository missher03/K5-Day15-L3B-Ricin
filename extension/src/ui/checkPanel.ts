import * as vscode from "vscode";
import * as crypto from "crypto";
import { ICodeOwnClient } from "../client/interface";
import { readCodeSnippet } from "../utils/codeSnippet";
import { getCheckHtml } from "./views/checkHtml";
import { getReflectHtml } from "./views/reflectHtml";

export class CheckPanel {
  public static currentPanel: CheckPanel | undefined;
  private readonly panel: vscode.WebviewPanel;
  private disposables: vscode.Disposable[] = [];

  public static async createOrShow(
    extensionUri: vscode.Uri,
    client: ICodeOwnClient,
    workspaceRoot: string,
    onSavedCallback?: () => void
  ) {
    const column = vscode.window.activeTextEditor
      ? vscode.window.activeTextEditor.viewColumn
      : undefined;

    if (CheckPanel.currentPanel) {
      CheckPanel.currentPanel.panel.reveal(column);
      return;
    }

    const panel = vscode.window.createWebviewPanel(
      "codeownCheck",
      "CodeOwn Check & Reflect",
      column || vscode.ViewColumn.One,
      {
        enableScripts: true,
        retainContextWhenHidden: true
      }
    );

    CheckPanel.currentPanel = new CheckPanel(panel, client, workspaceRoot, onSavedCallback);
  }

  private constructor(
    panel: vscode.WebviewPanel,
    private client: ICodeOwnClient,
    private workspaceRoot: string,
    private onSavedCallback?: () => void
  ) {
    this.panel = panel;
    this.panel.onDidDispose(() => this.dispose(), null, this.disposables);
    this.loadCheckFlow();
  }

  private async loadCheckFlow() {
    try {
      const checkStart = await this.client.checkStart();
      if (!checkStart.questions || checkStart.questions.length === 0) {
        this.loadReflectFlow();
        return;
      }
      const q = checkStart.questions[0];
      const snippet = readCodeSnippet(this.workspaceRoot, q.file, q.start_line, q.end_line);
      const nonce = crypto.randomBytes(16).toString("hex");

      this.panel.webview.html = getCheckHtml(nonce, checkStart.session_id, checkStart.commit_sha, q, snippet, 1);

      this.panel.webview.onDidReceiveMessage(
        async (msg) => {
          if (msg.command === "submitAnswer") {
            try {
              const res = await this.client.checkAnswer(msg.sessionId, msg.questionId, msg.answer);
              if (res.grade === "hieu" || res.round >= 2) {
                // Proceed to reflect flow
                await this.loadReflectFlow();
              } else {
                // Show round 2 with feedback & hint
                const hintText = res.hint ? `<p><strong>Gợi ý:</strong> ${res.hint}</p>` : "";
                const feedbackHtml = `<div class="card" style="border-left: 4px solid var(--vscode-charts-yellow);">
                  <h4>Kết quả: ${res.grade}</h4>
                  <p>${res.feedback}</p>
                  ${hintText}
                </div>`;
                this.panel.webview.html = getCheckHtml(nonce, msg.sessionId, checkStart.commit_sha, q, snippet, res.round) + feedbackHtml;
              }
            } catch (e: any) {
              vscode.window.showErrorMessage(`Lỗi khi nộp câu trả lời: ${e.message}`);
            }
          } else if (msg.command === "deferCheck") {
            this.panel.dispose();
          }
        },
        null,
        this.disposables
      );
    } catch (e: any) {
      this.panel.webview.html = `<!DOCTYPE html><html><body><h3>Lỗi tải Check: ${e.message}</h3></body></html>`;
    }
  }

  private async loadReflectFlow() {
    try {
      const reflect = await this.client.reflect();
      const nonce = crypto.randomBytes(16).toString("hex");

      this.panel.webview.html = getReflectHtml(nonce, reflect.reflect_markdown, reflect.sources);

      this.panel.webview.onDidReceiveMessage(
        async (msg) => {
          if (msg.command === "saveToLedger") {
            try {
              await this.client.ledgerSave("task_check_reflect", "Phản tư định kỳ từ Check", msg.markdown);
              vscode.window.showInformationMessage("Đã lưu vào Sổ kiến thức thành công!");
              if (this.onSavedCallback) {
                this.onSavedCallback();
              }
              this.panel.dispose();
            } catch (e: any) {
              vscode.window.showErrorMessage(`Lỗi khi lưu Sổ kiến thức: ${e.message}`);
            }
          }
        },
        null,
        this.disposables
      );
    } catch (e: any) {
      this.panel.webview.html = `<!DOCTYPE html><html><body><h3>Lỗi tải Reflect: ${e.message}</h3></body></html>`;
    }
  }

  public dispose() {
    CheckPanel.currentPanel = undefined;
    this.panel.dispose();
    while (this.disposables.length) {
      const x = this.disposables.pop();
      if (x) x.dispose();
    }
  }
}
