import { commonStyles } from "./commonStyles";

export function getReflectHtml(nonce: string, reflectMarkdown: string, sources: string[]): string {
  // Simple markdown formatting helper for display
  const htmlContent = reflectMarkdown
    .split("\n")
    .map(line => {
      if (line.startsWith("# ")) return `<h2>${line.substring(2)}</h2>`;
      if (line.startsWith("- ")) return `<li>${line.substring(2)}</li>`;
      if (line.trim() === "") return "<br/>";
      return `<p>${line}</p>`;
    })
    .join("");

  return `<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-${nonce}';">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CodeOwn Reflect</title>
  <style>${commonStyles}</style>
</head>
<body>
  <div class="card">
    <h3>Báo cáo Phản tư (Reflect)</h3>
    <div id="viewMode">
      <div id="markdownContent">${htmlContent}</div>
      <p><strong>Nguồn tham chiếu:</strong> ${sources.join(", ")}</p>
      <div style="display: flex; gap: 8px; margin-top: 12px;">
        <button id="editBtn" class="secondary">Chỉnh sửa</button>
        <button id="saveLedgerBtn">Lưu vào Sổ kiến thức</button>
      </div>
    </div>
    
    <div id="editMode" style="display: none;">
      <label for="editTextarea"><strong>Nội dung phản tư (Markdown):</strong></label>
      <textarea id="editTextarea" rows="10">${reflectMarkdown}</textarea>
      <div style="display: flex; gap: 8px; margin-top: 8px;">
        <button id="previewBtn" class="secondary">Xem trước</button>
        <button id="saveEditBtn">Lưu thay đổi</button>
      </div>
    </div>
  </div>

  <script nonce="${nonce}">
    const vscode = acquireVsCodeApi();
    const viewMode = document.getElementById('viewMode');
    const editMode = document.getElementById('editMode');
    const editBtn = document.getElementById('editBtn');
    const previewBtn = document.getElementById('previewBtn');
    const saveLedgerBtn = document.getElementById('saveLedgerBtn');
    const saveEditBtn = document.getElementById('saveEditBtn');
    const editTextarea = document.getElementById('editTextarea');
    const markdownContent = document.getElementById('markdownContent');

    editBtn.addEventListener('click', () => {
      viewMode.style.display = 'none';
      editMode.style.display = 'block';
    });

    previewBtn.addEventListener('click', () => {
      editMode.style.display = 'none';
      viewMode.style.display = 'block';
    });

    saveEditBtn.addEventListener('click', () => {
      const updated = editTextarea.value;
      vscode.postMessage({ command: 'updateReflect', markdown: updated });
      editMode.style.display = 'none';
      viewMode.style.display = 'block';
    });

    saveLedgerBtn.addEventListener('click', () => {
      saveLedgerBtn.disabled = true;
      saveLedgerBtn.textContent = 'Đang lưu...';
      vscode.postMessage({ command: 'saveToLedger', markdown: editTextarea.value });
    });
  </script>
</body>
</html>`;
}
