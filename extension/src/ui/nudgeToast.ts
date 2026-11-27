import * as vscode from "vscode";
import { ICodeOwnClient } from "../client/interface";
import { PendingNudge } from "../types";

export async function showNudgeToast(client: ICodeOwnClient, nudge: PendingNudge): Promise<void> {
  const msg = `CodeOwn (${nudge.file}:${nudge.line}): ${nudge.question}`;
  const actionReply = "Trả lời";
  const actionDismiss = "Bỏ qua";

  const selected = await vscode.window.showWarningMessage(msg, actionReply, actionDismiss);
  if (selected === actionReply) {
    const replyText = await vscode.window.showInputBox({
      prompt: "Nhập giả thuyết / giải thích 1 câu ngắn gọn",
      placeHolder: "Ví dụ: Dùng async/await để đảm bảo không block luồng chính..."
    });
    if (replyText !== undefined) {
      try {
        await client.ackNudge(nudge.id, "reply", replyText.trim());
        vscode.window.showInformationMessage("Đã ghi nhận câu trả lời cho Nudge.");
      } catch (e: any) {
        vscode.window.showErrorMessage(`Lỗi khi gửi phản hồi Nudge: ${e.message}`);
      }
    }
  } else if (selected === actionDismiss) {
    try {
      await client.ackNudge(nudge.id, "dismiss");
    } catch (e: any) {
      // ignore
    }
  }
}
