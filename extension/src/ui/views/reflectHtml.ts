import { escapeHtml } from "../../utils/html";
import { commonStyles } from "./commonStyles";

function renderMarkdownLines(markdown: string): string {
  const lines = markdown.split("\n");
  const out: string[] = [];
  let inList = false;

  for (const raw of lines) {
    const trimmed = raw.trim();
    if (!trimmed) {
      if (inList) {
        out.push("</ul>");
        inList = false;
      }
      continue;
    }
    const escaped = escapeHtml(trimmed).replace(
      /(\[(?:log#[^\]]+|docs:[^\]]+|[^:\]]+:\d+(?:-\d+)?)\])/g,
      '<span class="src">$1</span>'
    );
    if (trimmed.startsWith("- ")) {
      if (!inList) {
        out.push('<ul class="clean">');
        inList = true;
      }
      out.push(`<li>${escaped.slice(2)}</li>`);
    } else {
      if (inList) {
        out.push("</ul>");
        inList = false;
      }
      if (trimmed.startsWith("## ")) {
        out.push(`<h4>${escaped.slice(3)}</h4>`);
      } else if (trimmed.startsWith("# ")) {
        out.push(`<h3>${escaped.slice(2)}</h3>`);
      } else {
        out.push(`<p>${escaped}</p>`);
      }
    }
  }
  if (inList) out.push("</ul>");
  return out.join("\n");
}

// Render man hinh bao cao Reflect co nut Sua va Luu vao So
export function getReflectHtml(nonce: string, taskId: string, markdown: string, sources: string[]): string {
  const rendered = renderMarkdownLines(markdown);
  const srcList = sources.map((s) => `<code>${escapeHtml(s)}</code>`).join(" ");

  return `<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-${nonce}';">
  <title>CodeOwn: Reflect</title>
  <style>${commonStyles}</style>
</head>
<body>
  <div class="between">
    <h3>CodeOwn: Reflect · ${escapeHtml(taskId)}</h3>
    <span class="muted">Mọi khẳng định đều có nguồn</span>
  </div>
  <div class="card">
    <div id="viewMode">
      ${rendered}
      <p class="muted" style="margin-top:8px">Nguồn: ${srcList || "Không có"}</p>
    </div>
    <div id="editMode" class="hidden">
      <label for="editBox"><strong>Chỉnh sửa báo cáo (Markdown):</strong></label>
      <textarea id="editBox" rows="12">${escapeHtml(markdown)}</textarea>
    </div>
    <div class="row" style="margin-top:10px">
      <button id="saveBtn">Lưu vào Sổ</button>
      <button id="editBtn" class="secondary">Sửa báo cáo</button>
      <button class="secondary" disabled title="Mặc định tắt để bảo vệ riêng tư">Chia sẻ (đang tắt)</button>
    </div>
  </div>
  <script nonce="${nonce}">
    const vscode = acquireVsCodeApi();
    const viewMode = document.getElementById('viewMode');
    const editMode = document.getElementById('editMode');
    const editBtn = document.getElementById('editBtn');
    const saveBtn = document.getElementById('saveBtn');
    const editBox = document.getElementById('editBox');
    let editing = false;

    editBtn.addEventListener('click', () => {
      editing = !editing;
      viewMode.classList.toggle('hidden', editing);
      editMode.classList.toggle('hidden', !editing);
      editBtn.textContent = editing ? 'Xem lại' : 'Sửa báo cáo';
    });

    saveBtn.addEventListener('click', () => {
      saveBtn.disabled = true;
      saveBtn.textContent = 'Đang lưu...';
      vscode.postMessage({ command: 'saveToLedger', markdown: editBox.value });
    });
  </script>
</body>
</html>`;
}
