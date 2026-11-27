import * as vscode from "vscode";
import { ICodeOwnClient } from "../client/interface";
import { showNudgeToast } from "./nudgeToast";

export class StatusBarController {
  private statusBarItem: vscode.StatusBarItem;
  private timer: NodeJS.Timeout | undefined;
  private seenNudgeIds = new Set<string>();
  private seenCheckCommits = new Set<string>();
  private onStateUpdated?: () => void;

  constructor(private context: vscode.ExtensionContext, private clientProvider: () => ICodeOwnClient) {
    this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    this.statusBarItem.command = "codeown.openCheck";
    this.statusBarItem.text = "CodeOwn · DI 0";
    this.statusBarItem.show();
    context.subscriptions.push(this.statusBarItem);
  }

  public setOnStateUpdated(callback: () => void) {
    this.onStateUpdated = callback;
  }

  public startPolling() {
    const config = vscode.workspace.getConfiguration("codeown");
    const intervalSec = config.get<number>("pollIntervalSec") || 10;

    this.poll();
    this.timer = setInterval(() => {
      this.poll();
    }, intervalSec * 1000);

    this.context.subscriptions.push({
      dispose: () => {
        if (this.timer) clearInterval(this.timer);
      }
    });
  }

  public async poll() {
    try {
      const client = this.clientProvider();
      const status = await client.status();
      if (!status || !status.enabled) {
        this.statusBarItem.text = "CodeOwn (Tắt)";
        this.statusBarItem.backgroundColor = undefined;
        return;
      }

      const di = status.line_stats?.di || 0;
      this.statusBarItem.text = `CodeOwn · DI ${di.toFixed(0)}`;
      
      if (di > 70) {
        this.statusBarItem.backgroundColor = new vscode.ThemeColor("statusBarItem.warningBackground");
      } else {
        this.statusBarItem.backgroundColor = undefined;
      }

      // Check pending nudge
      if (status.pending_nudge && !this.seenNudgeIds.has(status.pending_nudge.id)) {
        this.seenNudgeIds.add(status.pending_nudge.id);
        await showNudgeToast(client, status.pending_nudge);
      }

      // Check pending check
      if (status.pending_check && !this.seenCheckCommits.has(status.pending_check.commit_sha)) {
        this.seenCheckCommits.add(status.pending_check.commit_sha);
        const actionOpen = "Mở Check";
        const actionLater = "Để sau";
        const sel = await vscode.window.showInformationMessage(
          `CodeOwn: Có Check mới cho commit ${status.pending_check.commit_sha.substring(0, 7)} (${status.pending_check.reason})`,
          actionOpen,
          actionLater
        );
        if (sel === actionOpen) {
          vscode.commands.executeCommand("codeown.openCheck");
        }
      }

      if (this.onStateUpdated) {
        this.onStateUpdated();
      }
    } catch {
      this.statusBarItem.text = "CodeOwn (Lỗi kết nối)";
    }
  }

  public dispose() {
    if (this.timer) clearInterval(this.timer);
  }
}
