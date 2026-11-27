import * as vscode from "vscode";
import { ICodeOwnClient } from "../client/interface";
import { PendingNudge } from "../types";
import { formatError } from "../utils/html";

// Hien thong bao nhac o goc duoi ben phai, cho phep tra loi hoac bo qua
export async function showNudgeToast(client: ICodeOwnClient, nudge: PendingNudge): Promise<void> {
  const nudgeId = nudge.id || nudge.event_id || `${nudge.rule}:${nudge.ts}`;
  const detail = nudge.metric_text ? ` (${nudge.metric_text})` : "";
  const msg = `CodeOwn${detail}: ${nudge.message}`;
  const actionReply = "Trả lời";
  const actionDismiss = "Bỏ qua";

  const selected = await vscode.window.showWarningMessage(msg, actionReply, actionDismiss);
  if (selected === actionReply) {
    const replyText = await vscode.window.showInputBox({
      prompt: "Bạn nghĩ lỗi do đâu? (1 câu ngắn gọn)",
      placeHolder: "Ví dụ: Do object lấy từ session khác nên delete bị lỗi..."
    });
    if (replyText !== undefined) {
      try {
        await client.ackNudge(nudgeId, "reply", replyText.trim());
        vscode.window.showInformationMessage("Đã ghi nhận câu trả lời.");
      } catch (err) {
        vscode.window.showErrorMessage(`Lỗi gửi phản hồi: ${formatError(err)}`);
      }
      return;
    }
  }

  if (selected === actionDismiss || selected === undefined) {
    try {
      await client.ackNudge(nudgeId, "dismiss");
    } catch {
      // Bo qua neu ack loi
    }
  }
}
