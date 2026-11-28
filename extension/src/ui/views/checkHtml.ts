import { CheckAnswerResult, CheckQuestion, GradeLabel } from "../../types";
import { escapeHtml } from "../../utils/html";
import { commonStyles } from "./commonStyles";

function labelText(label: GradeLabel): string {
  if (label === "hieu") return "Hiểu";
  if (label === "mot_phan") return "Một phần";
  return "Chưa hiểu";
}

// Render man hinh thong bao bo qua neu diff chua dat nguong Check
export function getCheckSkipHtml(reason: string): string {
  return `<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8"><style>${commonStyles}</style></head>
<body><div class="card"><h3>CodeOwn: Bỏ qua Check</h3><p>${escapeHtml(reason)}</p></div></body></html>`;
}

// Render man hinh cau hoi Check (ho tro nhieu cau va vong 2 follow-up)
export function getCheckHtml(params: {
  nonce: string;
  taskId: string;
  index: number;
  total: number;
  question: CheckQuestion;
  snippet: string;
  lastResult?: CheckAnswerResult;
}): string {
  const { nonce, taskId, index, total, question, snippet, lastResult } = params;
  const bars = Array.from({ length: total }, (_, i) => `<span class="${i <= index ? "on" : ""}"></span>`).join("");
  const [startL, endL] = question.lines;
  const isFollowUp = Boolean(lastResult && !lastResult.final && lastResult.follow_up);
  const canContinue = Boolean(lastResult && lastResult.final);

  let feedbackBlock = "";
  if (lastResult) {
    const missing = lastResult.missing_concept
      ? `<p><strong>Khái niệm còn hổng:</strong> ${escapeHtml(lastResult.missing_concept)}</p>`
      : "";
    const followUp = isFollowUp && lastResult.follow_up
      ? `<p><strong>Câu hỏi thêm (vòng 2):</strong> ${escapeHtml(lastResult.follow_up)}</p>`
      : "";
    feedbackBlock = `<div class="card">
      <div class="between">
        <strong>Kết quả chấm (Vòng ${lastResult.round}/2)</strong>
        <span class="chip ${lastResult.label}">${labelText(lastResult.label)}</span>
      </div>
      <p style="margin-top:6px">${escapeHtml(lastResult.hint)}</p>
      ${missing}
      ${followUp}
    </div>`;
  }

  const primaryAction = canContinue
    ? `<button id="nextBtn">${index + 1 < total ? "Câu tiếp theo" : "Xem báo cáo Reflect"}</button>`
    : `<button id="submitBtn">${isFollowUp ? "Gửi câu trả lời vòng 2" : "Gửi câu trả lời"}</button>
       <button id="skipBtn" class="secondary">${index + 1 < total ? "Sang câu tiếp theo" : "Xem báo cáo Reflect"}</button>
       <button id="deferBtn" class="secondary">Để sau</button>`;

  // Chuyen cau chu dong: giu nhan cua lan cham gan nhat (hoac "chua cham"), khong lo dap an.
  const skipNote = canContinue
    ? ""
    : `<p class="muted" style="margin-top:6px">${lastResult && lastResult.label
        ? `Sang câu tiếp sẽ giữ nhãn "${labelText(lastResult.label)}" cho câu này.`
        : "Sang câu tiếp: câu này giữ nhãn của lần chấm gần nhất; nếu chưa chấm lần nào thì ghi là chưa trả lời."}</p>`;

  const inputSection = canContinue
    ? `<div class="row">${primaryAction}</div>`
    : `<label for="answerText"><strong>Trả lời bằng lời của bạn (không dán code):</strong></label>
       <textarea id="answerText" rows="4" placeholder="Giải thích ngắn gọn cơ chế đoạn code này..."></textarea>
       <div class="row" style="margin-top:6px">${primaryAction}</div>
       ${skipNote}`;

  return `<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-${nonce}';">
  <title>CodeOwn: Check</title>
  <style>${commonStyles}</style>
</head>
<body>
  <div class="between">
    <h3>CodeOwn: Check · ${escapeHtml(taskId)}</h3>
    <span class="muted">Câu ${index + 1} / ${total}</span>
  </div>
  <div class="prog">${bars}</div>
  <div class="card">
    <div class="between">
      <span class="src">${escapeHtml(question.file)}:${startL}-${endL}</span>
      <span class="muted">${escapeHtml(question.concept)}</span>
    </div>
    <pre><code>${escapeHtml(snippet)}</code></pre>
    <p><strong>${escapeHtml(question.question)}</strong></p>
  </div>
  ${feedbackBlock}
  <div class="card">${inputSection}</div>
  <script nonce="${nonce}">
    const vscode = acquireVsCodeApi();
    const submitBtn = document.getElementById('submitBtn');
    const deferBtn = document.getElementById('deferBtn');
    const nextBtn = document.getElementById('nextBtn');
    const skipBtn = document.getElementById('skipBtn');
    const answerEl = document.getElementById('answerText');
    if (submitBtn && answerEl) {
      submitBtn.addEventListener('click', () => {
        const text = answerEl.value.trim();
        if (!text) return;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Đang chấm...';
        vscode.postMessage({ command: 'submitAnswer', qid: '${escapeHtml(question.qid)}', text });
      });
    }
    if (deferBtn) {
      deferBtn.addEventListener('click', () => vscode.postMessage({ command: 'deferCheck' }));
    }
    if (skipBtn) {
      skipBtn.addEventListener('click', () => vscode.postMessage({ command: 'nextQuestion' }));
    }
    if (nextBtn) {
      nextBtn.addEventListener('click', () => vscode.postMessage({ command: 'nextQuestion' }));
    }
  </script>
</body>
</html>`;
}
