import { commonStyles } from "./commonStyles";

export function getSidebarHtml(nonce: string, statusData: any, ledgerItems: any[]): string {
  const di = statusData?.line_stats?.di || 0;
  const total = statusData?.line_stats?.total || 0;
  const covered = statusData?.line_stats?.covered || 0;
  const commit = statusData?.commit ? statusData.commit.substring(0, 7) : "N/A";
  const repo = statusData?.repo || "vin-ai-lab";

  const nudgeHtml = statusData?.pending_nudge
    ? `<div class="card" style="border-left: 4px solid var(--vscode-charts-orange);">
        <h4>Nudge đang chờ</h4>
        <p><strong>${statusData.pending_nudge.file}:${statusData.pending_nudge.line}</strong></p>
        <p>${statusData.pending_nudge.question}</p>
        <button id="replyNudgeBtn" style="padding: 4px 8px; font-size: 11px;">Trả lời nhanh</button>
       </div>`
    : `<p><em>Không có Nudge chờ xử lý.</em></p>`;

  const ledgerHtml = ledgerItems.length > 0
    ? ledgerItems.slice(0, 5).map(item => `
        <div class="card" style="padding: 8px; margin-bottom: 6px;">
          <p style="margin: 0; font-weight: bold; font-size: 12px;">${item.summary}</p>
          <p style="margin: 2px 0 0 0; font-size: 11px; opacity: 0.8;">Task: ${item.task_id} | ${new Date(item.timestamp).toLocaleDateString()}</p>
        </div>
      `).join("")
    : `<p><em>Chưa có mục nào trong sổ kiến thức.</em></p>`;

  return `<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-${nonce}';">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CodeOwn Sidebar</title>
  <style>${commonStyles}</style>
</head>
<body>
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
    <h3 style="margin: 0;">CodeOwn</h3>
    <span class="badge ${di > 70 ? 'badge-chua-hieu' : 'badge-hieu'}">DI: ${di.toFixed(1)}</span>
  </div>

  <div class="card">
    <p style="margin: 4px 0;"><strong>Repo:</strong> ${repo}</p>
    <p style="margin: 4px 0;"><strong>Commit:</strong> ${commit}</p>
    <p style="margin: 4px 0;"><strong>Dòng code:</strong> ${covered}/${total} đã bao phủ</p>
  </div>

  <div style="display: flex; gap: 6px; margin-bottom: 12px;">
    <button id="openCheckBtn" style="flex: 1; padding: 6px;">Mở Check</button>
    <button id="refreshBtn" class="secondary" style="padding: 6px;">Làm mới</button>
  </div>

  <div class="card" style="padding: 8px; margin-bottom: 12px;">
    <button id="apiKeyBtn" class="secondary" style="width: 100%; font-size: 11px;">Nhập / Cập nhật API Key</button>
  </div>

  <div>
    <h4 style="margin-bottom: 6px;">Nudge gần đây</h4>
    ${nudgeHtml}
  </div>

  <div style="margin-top: 16px;">
    <h4 style="margin-bottom: 6px;">Sổ kiến thức gần đây</h4>
    ${ledgerHtml}
  </div>

  <script nonce="${nonce}">
    const vscode = acquireVsCodeApi();
    document.getElementById('openCheckBtn').addEventListener('click', () => {
      vscode.postMessage({ command: 'openCheck' });
    });
    document.getElementById('refreshBtn').addEventListener('click', () => {
      vscode.postMessage({ command: 'refresh' });
    });
    document.getElementById('apiKeyBtn').addEventListener('click', () => {
      vscode.postMessage({ command: 'setApiKey' });
    });
    const replyBtn = document.getElementById('replyNudgeBtn');
    if (replyBtn) {
      replyBtn.addEventListener('click', () => {
        vscode.postMessage({ command: 'replyNudge' });
      });
    }
  </script>
</body>
</html>`;
}
