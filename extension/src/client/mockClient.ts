import {
  CheckAnswerResult,
  CheckStartResult,
  InitResult,
  LedgerListResult,
  OkResult,
  PendingNudge,
  ReflectResult,
  StatusResult
} from "../types";
import { ICodeOwnClient } from "./interface";
import {
  INITIAL_LEDGER_ITEMS,
  INITIAL_NUDGES,
  INITIAL_PENDING_NUDGE,
  MOCK_QUESTIONS,
  MOCK_REFLECT_MARKDOWN
} from "./mockData";

// Du lieu gia lap theo dung hop dong de test giao dien khong can loi Python
export class MockCodeOwnClient implements ICodeOwnClient {
  private roundByQid = new Map<string, number>();
  private pendingNudge: PendingNudge | null = { ...INITIAL_PENDING_NUDGE };
  private ledgerItems = [...INITIAL_LEDGER_ITEMS];
  private recentNudges = [...INITIAL_NUDGES];

  async init(_repoPath: string, _rulesOnly?: boolean): Promise<InitResult> {
    return {
      hooks_written: [".claude/settings.json", ".git/hooks/post-commit"],
      gitignore_updated: true
    };
  }

  async status(): Promise<StatusResult> {
    return {
      task_id: "t_20261127_01",
      task_title: "feat/todo-delete",
      di: 64,
      stats: { ai_giu_nguyen: 27, ai_da_sua: 3, nguoi_viet: 4 },
      pending_nudge: this.pendingNudge,
      pending_check: {
        task_id: "t_20261127_01",
        commit: "3f2a1c9",
        commit_msg: "add delete todo",
        ai_lines: 30,
        total_lines: 34,
        question_count: 3
      }
    };
  }

  async ackNudge(nudgeId: string, action: "reply" | "dismiss", replyText?: string): Promise<OkResult> {
    if (this.pendingNudge && this.pendingNudge.id === nudgeId) {
      this.recentNudges.unshift({
        ts: new Date().toISOString(),
        rule: this.pendingNudge.rule,
        summary: replyText ? `Trả lời: ${replyText}` : "Dán cùng lỗi 3 lần",
        action
      });
      this.pendingNudge = null;
    }
    return { ok: true };
  }

  async checkStart(taskId: string): Promise<CheckStartResult> {
    this.roundByQid.clear();
    return { task_id: taskId, questions: MOCK_QUESTIONS };
  }

  async checkAnswer(_taskId: string, qid: string, text: string): Promise<CheckAnswerResult> {
    const round = (this.roundByQid.get(qid) ?? 0) + 1;
    this.roundByQid.set(qid, round);

    const normalized = text.trim().toLowerCase();
    if (qid === "q1" && round === 1 && normalized.length < 40) {
      return {
        qid,
        label: "mot_phan",
        confidence: 0.62,
        missing_concept: "Mã HTTP 500 khi ngoại lệ không được bắt",
        hint: "Nghĩ thử: khi `db.delete(None)` ném lỗi ở dòng 43 và không có try/except, framework trả mã nào?",
        follow_up: "`db.delete(None)` ném lỗi ở dòng mấy, và client nhận mã 404 hay 500?",
        round: 1,
        final: false
      };
    }

    if (qid === "q3" && (normalized.includes("chưa") || normalized.includes("không biết"))) {
      return {
        qid,
        label: "chua_hieu",
        confidence: 0.88,
        missing_concept: "Vòng đời generator dependency trong FastAPI",
        hint: "Xem lại từ khoá `yield` trong `get_db()` và cơ chế `finally` khi hàm route kết thúc.",
        follow_up: null,
        round,
        final: true
      };
    }

    return {
      qid,
      label: "hieu",
      confidence: 0.91,
      missing_concept: null,
      hint: "Bạn đã giải thích đúng cơ chế vận hành của đoạn code này.",
      follow_up: null,
      round,
      final: true
    };
  }

  async reflect(_taskId: string): Promise<ReflectResult> {
    return {
      markdown: MOCK_REFLECT_MARKDOWN,
      sources: ["log#ev_01", "log#ev_04", "app/routes.py:41-45", "docs:fastapi-dependencies"]
    };
  }

  async ledgerSave(taskId: string, _markdown?: string): Promise<OkResult> {
    this.ledgerItems.unshift({
      ts: new Date().toISOString(),
      task_id: taskId,
      concept: "Xử lý ca không tìm thấy & Session",
      label: "hieu"
    });
    return { ok: true };
  }

  async ledgerList(): Promise<LedgerListResult> {
    return { items: this.ledgerItems, recent_nudges: this.recentNudges };
  }
}
