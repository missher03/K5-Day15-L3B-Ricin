import * as fs from "fs";
import * as path from "path";
import { GradeLabel, LedgerItem, LedgerListResult, NudgeHistoryItem, PendingCheck } from "../types";

function toGradeLabel(value: unknown): GradeLabel {
  if (value === "hieu" || value === "mot_phan" || value === "chua_hieu") {
    return value;
  }
  return "mot_phan";
}

function parseJsonLines(filePath: string): Record<string, unknown>[] {
  if (!fs.existsSync(filePath)) {
    return [];
  }
  const rows: Record<string, unknown>[] = [];
  const lines = fs.readFileSync(filePath, "utf8").split("\n");
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) {
      continue;
    }
    try {
      const parsed: unknown = JSON.parse(trimmed);
      if (parsed && typeof parsed === "object") {
        rows.push(parsed as Record<string, unknown>);
      }
    } catch {
      // Bo qua dong JSON loi
    }
  }
  return rows;
}

// Doc du phong tu .codeown/ledger.jsonl va .codeown/events.jsonl khi CLI chua co ledger list
export function readLocalFallbackLedger(workspaceRoot: string): LedgerListResult {
  const codeownDir = path.join(workspaceRoot, ".codeown");
  const ledgerRows = parseJsonLines(path.join(codeownDir, "ledger.jsonl"));
  const items: LedgerItem[] = ledgerRows.map((row) => ({
    ts: typeof row.ts === "string" ? row.ts : new Date().toISOString(),
    task_id: typeof row.task_id === "string" ? row.task_id : "chua_ro",
    concept: typeof row.concept === "string" ? row.concept : "Khái niệm đã lưu",
    label: toGradeLabel(row.label),
    next_step: typeof row.next_step === "string" ? row.next_step : undefined
  }));

  const eventRows = parseJsonLines(path.join(codeownDir, "events.jsonl"));
  const recentNudges: NudgeHistoryItem[] = [];
  for (const row of eventRows) {
    if (row.event !== "nudge") {
      continue;
    }
    const meta = (row.meta && typeof row.meta === "object" ? row.meta : {}) as Record<string, unknown>;
    recentNudges.push({
      ts: typeof row.ts === "string" ? row.ts : "",
      rule: typeof meta.rule === "string" ? meta.rule : "nudge",
      summary: typeof meta.summary === "string" ? meta.summary : "Nhắc kiểm tra code",
      action: meta.action === "reply" ? "reply" : "dismiss"
    });
  }

  return {
    items: items.reverse(),
    recent_nudges: recentNudges.reverse().slice(0, 5)
  };
}

// Doc commit moi nhat tu .codeown/summary.jsonl de kich hoat thong bao Check
export function readLatestPendingCheck(workspaceRoot: string): PendingCheck | null {
  const summaryPath = path.join(workspaceRoot, ".codeown", "summary.jsonl");
  const rows = parseJsonLines(summaryPath);
  if (rows.length === 0) {
    return null;
  }
  const last = rows[rows.length - 1];
  const commit = typeof last.commit === "string" ? last.commit : "";
  if (!commit) {
    return null;
  }
  const stats = (last.stats && typeof last.stats === "object" ? last.stats : {}) as Record<string, unknown>;
  const aiKeep = typeof stats.ai_giu_nguyen === "number" ? stats.ai_giu_nguyen : 0;
  const aiEdit = typeof stats.ai_da_sua === "number" ? stats.ai_da_sua : 0;
  const human = typeof stats.nguoi_viet === "number" ? stats.nguoi_viet : 0;
  const aiLines = aiKeep + aiEdit;
  const totalLines = aiLines + human;
  if (aiLines < 20 && (totalLines === 0 || aiLines / totalLines < 0.3)) {
    return null;
  }
  const di = typeof last.di === "number" ? last.di : 0;
  const questionCount = di > 70 ? 5 : di >= 40 ? 3 : 2;
  return {
    task_id: typeof last.task_id === "string" ? last.task_id : "current",
    commit,
    commit_msg: commit.slice(0, 7),
    ai_lines: aiLines,
    total_lines: totalLines,
    question_count: questionCount
  };
}
