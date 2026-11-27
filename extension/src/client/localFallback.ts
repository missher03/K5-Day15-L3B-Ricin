import * as fs from "fs";
import * as path from "path";
import { LedgerItem, LedgerListResult, StatusResult } from "../types";

export function readLocalFallbackLedger(workspaceRoot: string): LedgerListResult {
  const ledgerPath = path.join(workspaceRoot, ".codeown", "ledger.jsonl");
  const items: LedgerItem[] = [];
  try {
    if (fs.existsSync(ledgerPath)) {
      const content = fs.readFileSync(ledgerPath, "utf8");
      const lines = content.split("\n");
      for (const line of lines) {
        if (!line.trim()) continue;
        try {
          const parsed = JSON.parse(line);
          items.push({
            id: parsed.id || parsed.task_id || "item_1",
            timestamp: parsed.timestamp || new Date().toISOString(),
            task_id: parsed.task_id || parsed.id || "task_0",
            summary: parsed.summary || parsed.title || "Kien thuc da luu",
            details: parsed.details || parsed.description
          });
        } catch {
          // ignore invalid json line
        }
      }
    }
  } catch {
    // fallback empty
  }
  return { items };
}

export function readLocalFallbackStatus(workspaceRoot: string): Partial<StatusResult> {
  const eventsPath = path.join(workspaceRoot, ".codeown", "events.jsonl");
  try {
    if (fs.existsSync(eventsPath)) {
      // can inspect events if needed
    }
  } catch {
    // ignore
  }
  return {};
}
