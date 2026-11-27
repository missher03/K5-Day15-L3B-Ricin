import * as vscode from "vscode";
import { ICodeOwnClient } from "../client/interface";
import { StatusResult } from "../types";
import { showNudgeToast } from "./nudgeToast";

// Quan ly thanh trang thai DI va polling dinh ky
export class StatusBarController {
  private statusBarItem: vscode.StatusBarItem;
  private timer: NodeJS.Timeout | undefined;
  private seenNudgeIds = new Set<string>();
  private seenCheckCommits = new Set<string>();
  private lastStatus: StatusResult | undefined;
  private onStateUpdated?: () => void;

  constructor(
    private context: vscode.ExtensionContext,
    private clientProvider: () => ICodeOwnClient
  ) {
    this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    this.statusBarItem.command = "codeown.openLedger";
    this.statusBarItem.text = "CodeOwn · DI --";
    this.statusBarItem.tooltip = "Bấm để mở Sổ kiến thức CodeOwn";
    this.statusBarItem.show();
    context.subscriptions.push(this.statusBarItem);
  }

  public getLastTaskId(): string {
    return this.lastStatus?.task_id || "current";
  }

  public setOnStateUpdated(callback: () => void): void {
    this.onStateUpdated = callback;
  }

  public startPolling(): void {
    const config = vscode.workspace.getConfiguration("codeown");
    const intervalSec = Math.max(3, config.get<number>("pollIntervalSec") ?? 10);

    void this.poll();
    this.timer = setInterval(() => {
      void this.poll();
    }, intervalSec * 1000);

    this.context.subscriptions.push({
      dispose: () => this.dispose()
    });
  }

  public async poll(): Promise<void> {
    try {
      const client = this.clientProvider();
      const status = await client.status();
      this.lastStatus = status;

      const diVal = status.di;
      const diText = diVal === null || diVal === undefined ? "--" : String(Math.round(diVal));
      this.statusBarItem.text = `CodeOwn · DI ${diText}`;
      this.statusBarItem.tooltip =
        `Task: ${status.task_title || status.task_id}\n` +
        `AI giữ nguyên: ${status.stats.ai_giu_nguyen} · AI sửa: ${status.stats.ai_da_sua} · Bạn viết: ${status.stats.nguoi_viet}`;
      this.statusBarItem.backgroundColor =
        typeof diVal === "number" && diVal > 70
          ? new vscode.ThemeColor("statusBarItem.warningBackground")
          : undefined;

      if (status.pending_nudge) {
        const nudgeKey = status.pending_nudge.id || status.pending_nudge.event_id || `${status.pending_nudge.rule}:${status.pending_nudge.ts}`;
        if (!this.seenNudgeIds.has(nudgeKey)) {
          this.seenNudgeIds.add(nudgeKey);
          await showNudgeToast(client, status.pending_nudge);
        }
      }

      if (status.pending_check && !this.seenCheckCommits.has(status.pending_check.commit)) {
        const pc = status.pending_check;
        this.seenCheckCommits.add(pc.commit);
        const msg = `CodeOwn: Sau commit "${pc.commit_msg}", AI viết ${pc.ai_lines}/${pc.total_lines} dòng (DI ${diText}). Trả lời ${pc.question_count} câu?`;
        const choice = await vscode.window.showInformationMessage(msg, "Mở Check", "Để sau");
        if (choice === "Mở Check") {
          void vscode.commands.executeCommand("codeown.openCheck");
        }
      }

      this.onStateUpdated?.();
    } catch {
      this.statusBarItem.text = "CodeOwn · Chưa bật";
      this.statusBarItem.backgroundColor = undefined;
    }
  }

  public dispose(): void {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = undefined;
    }
  }
}
