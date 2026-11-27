import { commonStyles } from "./commonStyles";

export function getCheckHtml(nonce: string, sessionId: string, commitSha: string, question: any, snippet: string, round: number): string {
  return `<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-${nonce}';">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CodeOwn Check</title>
  <style>${commonStyles}</style>
</head>
<body>
  <div class="card">
    <h3>Kiểm tra hiểu biết · Commit ${commitSha.substring(0, 7)}</h3>
    <p><strong>Phiên ID:</strong> ${sessionId} | <strong>Vòng:</strong> ${round}/2</p>
    <p><strong>Câu hỏi (${question.question_id}):</strong> ${question.question}</p>
    <p><code>${question.file}:${question.start_line}-${question.end_line}</code></p>
    <pre><code>${snippet}</code></pre>
    ${question.context_hint ? `<p><em>Gợi ý: ${question.context_hint}</em></p>` : ""}
  </div>

  <div class="card">
    <label for="answerText"><strong>Giải thích / Trả lời của bạn:</strong></label>
    <textarea id="answerText" rows="5" placeholder="Nhập câu trả lời chi tiết..."></textarea>
    <div style="display: flex; gap: 8px; margin-top: 8px;">
      <button id="submitBtn">Nộp câu trả lời</button>
      <button id="deferBtn" class="secondary">Để sau</button>
    </div>
  </div>

  <div id="resultArea"></div>

  <script nonce="${nonce}">
    const vscode = acquireVsCodeApi();
    const submitBtn = document.getElementById('submitBtn');
    const deferBtn = document.getElementById('deferBtn');
    const answerText = document.getElementById('answerText');

    submitBtn.addEventListener('click', () => {
      const text = answerText.value.trim();
      if (!text) {
        alert('Vui lòng nhập câu trả lời.');
        return;
      }
      submitBtn.disabled = true;
      submitBtn.textContent = 'Đang chấm...';
      vscode.postMessage({
        command: 'submitAnswer',
        sessionId: '${sessionId}',
        questionId: '${question.question_id}',
        answer: text
      });
    });

    deferBtn.addEventListener('click', () => {
      vscode.postMessage({ command: 'deferCheck' });
    });
  </script>
</body>
</html>`;
}
