import * as crypto from "crypto";
import * as vscode from "vscode";
import { ICodeOwnClient } from "../client/interface";
import { CheckAnswerResult, CheckQuestion } from "../types";
import { readCodeSnippet } from "../utils/codeSnippet";
import { escapeHtml, formatError } from "../utils/html";
import { getCheckHtml, getCheckSkipHtml } from "./views/checkHtml";
import { getReflectHtml } from "./views/reflectHtml";

interface WebviewMsg {
  command?: string;
  qid?: string;
  text?: string;
  markdown?: string;
}

// Dieu phoi tab Check -> Reflect trong editor
export class CheckPanel {
  public static currentPanel: CheckPanel | undefined;
  private readonly panel: vscode.WebviewPanel;
  private disposables: vscode.Disposable[] = [];
  private questions: CheckQuestion[] = [];
  private currentIndex = 0;
  private lastResult: CheckAnswerResult | undefined;

  public static async createOrShow(
    client: ICodeOwnClient,
    workspaceRoot: string,
    taskId: string,
    onSaved?: () => void
  ): Promise<void> {
    const column = vscode.window.activeTextEditor?.viewColumn ?? vscode.ViewColumn.One;
    if (CheckPanel.currentPanel) {
      CheckPanel.currentPanel.panel.reveal(column);
      await CheckPanel.currentPanel.startSession(taskId);
      return;
    }

    const panel = vscode.window.createWebviewPanel(
      "codeownCheck",
      "CodeOwn: Check",
      column,
      { enableScripts: true, retainContextWhenHidden: true }
    );
    CheckPanel.currentPanel = new CheckPanel(panel, client, workspaceRoot, taskId, onSaved);
  }

  private constructor(
    panel: vscode.WebviewPanel,
    private client: ICodeOwnClient,
    private workspaceRoot: string,
    private taskId: string,
    private onSaved?: () => void
  ) {
    this.panel = panel;
    this.panel.onDidDispose(() => this.dispose(), null, this.disposables);
    this.panel.webview.onDidReceiveMessage(
      (msg: WebviewMsg) => void this.handleMessage(msg),
      null,
      this.disposables
    );
    void this.startSession(taskId);
  }

  private async startSession(taskId: string): Promise<void> {
    this.taskId = taskId;
    this.currentIndex = 0;
    this.lastResult = undefined;
    try {
      const start = await this.client.checkStart(taskId);
      if ("skip" in start) {
        this.panel.webview.html = getCheckSkipHtml(start.skip);
        return;
      }
      this.taskId = start.task_id || taskId;
      this.questions = start.questions;
      if (this.questions.length === 0) {
        await this.showReflect();
        return;
      }
      this.renderCurrentQuestion();
    } catch (err) {
      this.panel.webview.html = `<p>Lỗi tải Check: ${escapeHtml(formatError(err))}</p>`;
    }
  }

  private renderCurrentQuestion(): void {
    const q = this.questions[this.currentIndex];
    const snippet = readCodeSnippet(this.workspaceRoot, q.file, q.lines);
    const nonce = crypto.randomBytes(16).toString("hex");
    this.panel.title = "CodeOwn: Check";
    this.panel.webview.html = getCheckHtml({
      nonce,
      taskId: this.taskId,
      index: this.currentIndex,
      total: this.questions.length,
      question: q,
      snippet,
      lastResult: this.lastResult
    });
  }

  private async showReflect(): Promise<void> {
    try {
      const reflect = await this.client.reflect(this.taskId);
      const nonce = crypto.randomBytes(16).toString("hex");
      this.panel.title = "CodeOwn: Reflect";
      this.panel.webview.html = getReflectHtml(nonce, this.taskId, reflect.markdown, reflect.sources);
    } catch (err) {
      this.panel.webview.html = `<p>Lỗi tải Reflect: ${escapeHtml(formatError(err))}</p>`;
    }
  }

  private async handleMessage(msg: WebviewMsg): Promise<void> {
    if (msg.command === "deferCheck") {
      this.panel.dispose();
      return;
    }

    if (msg.command === "submitAnswer" && msg.qid && msg.text) {
      try {
        this.lastResult = await this.client.checkAnswer(this.taskId, msg.qid, msg.text);
        this.renderCurrentQuestion();
      } catch (err) {
        vscode.window.showErrorMessage(`Lỗi chấm câu trả lời: ${formatError(err)}`);
      }
      return;
    }

    if (msg.command === "nextQuestion") {
      this.lastResult = undefined;
      if (this.currentIndex + 1 < this.questions.length) {
        this.currentIndex += 1;
        this.renderCurrentQuestion();
      } else {
        await this.showReflect();
      }
      return;
    }

    if (msg.command === "saveToLedger") {
      try {
        await this.client.ledgerSave(this.taskId, msg.markdown);
        vscode.window.showInformationMessage("Đã lưu báo cáo vào Sổ kiến thức.");
        this.onSaved?.();
        this.panel.dispose();
      } catch (err) {
        vscode.window.showErrorMessage(`Lỗi lưu Sổ kiến thức: ${formatError(err)}`);
      }
    }
  }

  public dispose(): void {
    CheckPanel.currentPanel = undefined;
    while (this.disposables.length) {
      this.disposables.pop()?.dispose();
    }
  }
}
