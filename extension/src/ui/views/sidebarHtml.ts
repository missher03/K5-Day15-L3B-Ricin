import { GradeLabel, LedgerItem, NudgeHistoryItem, StatusResult } from "../../types";
import { escapeHtml } from "../../utils/html";
import { commonStyles } from "./commonStyles";

function diLevel(di: number | null): { cls: string; text: string } {
  if (di === null) return { cls: "hieu", text: "chưa có" };
  if (di > 70) return { cls: "chua_hieu", text: "cao" };
  if (di >= 40) return { cls: "mot_phan", text: "vừa" };
  return { cls: "hieu", text: "thấp" };
}

function labelBadge(label: GradeLabel): string {
  if (label === "hieu") return '<span class="chip hieu">hiểu</span>';
  if (label === "mot_phan") return '<span class="chip mot_phan">một phần</span>';
  return '<span class="chip chua_hieu">chưa hiểu</span>';
}

// Render giao dien Sidebar gom 4 khoi: Task/DI, Ti le dong, Nhac, So kien thuc
export function getSidebarHtml(
  nonce: string,
  status: StatusResult | null,
  items: LedgerItem[],
  nudges: NudgeHistoryItem[]
): string {
  const diVal = status?.di ?? null;
  const diText = diVal === null ? "--" : String(Math.round(diVal));
  const lvl = diLevel(diVal);
  const s = status?.stats ?? { ai_giu_nguyen: 0, ai_da_sua: 0, nguoi_viet: 0 };
  const total = Math.max(1, s.ai_giu_nguyen + s.ai_da_sua + s.nguoi_viet);
  const pctAi = Math.round((s.ai_giu_nguyen / total) * 100);
  const pctEdit = Math.round((s.ai_da_sua / total) * 100);
  const pctMe = Math.max(0, 100 - pctAi - pctEdit);

  const nudgeRows = nudges.length
    ? nudges.slice(0, 4).map((n) => `
      <div class="between" style="margin-bottom:4px">
        <span class="muted">${escapeHtml(n.summary)}</span>
        <span class="chip ${n.action === "reply" ? "hieu" : "mot_phan"}">${n.action === "reply" ? "đã trả lời" : "bỏ qua"}</span>
      </div>`).join("")
    : '<p class="muted">Chưa có lần nhắc nào.</p>';

  const ledgerRows = items.length
    ? items.slice(0, 6).map((item) => `
      <div class="between" style="margin-bottom:6px">
        <span>${escapeHtml(item.concept)}</span>
        ${labelBadge(item.label)}
      </div>`).join("")
    : '<p class="muted">Sổ kiến thức chưa có mục nào.</p>';

  return `<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-${nonce}';">
  <title>CodeOwn</title>
  <style>${commonStyles}</style>
</head>
<body class="sidebar-body">
  <div class="card">
    <div class="muted">Task đang làm</div>
    <p><strong>${escapeHtml(status?.task_title || status?.task_id || "Chưa bật")}</strong></p>
    <div class="between">
      <span style="font-size:20px;font-weight:700">DI ${diText}</span>
      <span class="chip ${lvl.cls}">${lvl.text}</span>
    </div>
  </div>

  <div class="card">
    <div class="muted">Tỉ lệ dòng code</div>
    <div class="split">
      <i class="ai" style="width:${pctAi}%"></i>
      <i class="ed" style="width:${pctEdit}%"></i>
      <i class="me" style="width:${pctMe}%"></i>
    </div>
    <div class="muted">AI giữ nguyên ${s.ai_giu_nguyen} · Bạn sửa ${s.ai_da_sua} · Bạn viết ${s.nguoi_viet}</div>
  </div>

  <div class="row" style="margin-bottom:10px">
    <button id="checkBtn" style="flex:1">Mở Check</button>
    <button id="refreshBtn" class="secondary">Làm mới</button>
    <button id="keyBtn" class="secondary">API Key</button>
  </div>

  <div class="card">
    <h4>Nhắc trong task</h4>
    ${nudgeRows}
  </div>

  <div class="card">
    <h4>Sổ kiến thức</h4>
    ${ledgerRows}
  </div>

  <script nonce="${nonce}">
    const vscode = acquireVsCodeApi();
    document.getElementById('checkBtn').addEventListener('click', () => vscode.postMessage({ command: 'openCheck' }));
    document.getElementById('refreshBtn').addEventListener('click', () => vscode.postMessage({ command: 'refresh' }));
    document.getElementById('keyBtn').addEventListener('click', () => vscode.postMessage({ command: 'setApiKey' }));
  </script>
</body>
</html>`;
}
