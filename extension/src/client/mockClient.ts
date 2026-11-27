import { ICodeOwnClient } from "./interface";
import {
  InitResult,
  StatusResult,
  CheckStartResult,
  CheckAnswerResult,
  ReflectResult,
  LedgerListResult,
  OkResult
} from "../types";

export class MockCodeOwnClient implements ICodeOwnClient {
  private ledgerItems: LedgerItemModel[] = [
    {
      id: "ledger_01",
      timestamp: "2026-11-27T08:00:00Z",
      task_id: "task_01",
      summary: "Hieu ro cau truc routing trong app/routes.py",
      details: "Da nam vung co che decorator va xu ly request async."
    },
    {
      id: "ledger_02",
      timestamp: "2026-11-27T08:30:00Z",
      task_id: "task_02",
      summary: "Xu ly loi xac thuc trong codebase/ai.py",
      details: "Su dung usage cua API thay vi uoc luong token."
    }
  ];

  async init(_rulesOnly?: boolean): Promise<InitResult> {
    return {
      status: "ok",
      repo: "vin-ai-lab"
    };
  }

  async status(): Promise<StatusResult> {
    return {
      enabled: true,
      repo: "vin-ai-lab",
      commit: "c7367d7",
      line_stats: {
        total: 1250,
        covered: 980,
        uncovered: 270,
        di: 21.6
      },
      pending_nudge: {
        id: "ev_01",
        commit_sha: "c7367d7",
        file: "codebase/agent.py",
        line: 42,
        question: "Tai sao dung answer(text) thay vi dict truc tiep?",
        timestamp: "2026-11-27T09:00:00Z"
      },
      pending_check: {
        commit_sha: "c7367d7",
        files: ["codebase/agent.py", "codebase/ai.py"],
        reason: "Da co thay doi quan trong can kiem tra hieu biet."
      }
    };
  }

  async ackNudge(_nudgeId: string, _action: "reply" | "dismiss", _replyText?: string): Promise<OkResult> {
    return { status: "ok" };
  }

  async checkStart(): Promise<CheckStartResult> {
    return {
      session_id: "mock_session_123",
      commit_sha: "c7367d7",
      questions: [
        {
          question_id: "q1",
          file: "codebase/agent.py",
          start_line: 38,
          end_line: 45,
          question: "Giai thich cach ham answer(text) xu ly dau vao va dam bao dung cau truc spec.md §4?",
          context_hint: "Xem ky cach goi call_model va dinh dang tra ve {'output': str}"
        },
        {
          question_id: "q2",
          file: "codebase/ai.py",
          start_line: 12,
          end_line: 28,
          question: "Tai sao token phai lay tu usage cua API ma khong duoc uoc luong?",
          context_hint: "Dam bao tinh chinh xac chi phi va tuan thu luat"
        }
      ]
    };
  }

  async checkAnswer(_sessionId: string, _questionId: string, answer: string): Promise<CheckAnswerResult> {
    if (answer.toLowerCase().includes("chua")) {
      return {
        grade: "chua_hieu",
        feedback: "Cau tra loi chua chinh xac hoac thieu y cot loi ve hop dong ham.",
        missing_concept: "Hop dong ham va usage API",
        hint: "Doc lai spec.md §4 va codebase/ai.py de nam ro quy dinh.",
        round: 2
      };
    }
    return {
      grade: "hieu",
      feedback: "Tuyet voi! Ban da hieu dung ban chat cua van de.",
      round: 1
    };
  }

  async reflect(): Promise<ReflectResult> {
    return {
      reflect_markdown: "# Tom tat phien lam viec\n\nTrong phien nay, ban da nam vung cau truc `answer(text)` [log#ev_01] va co che lay token [codebase/ai.py:15].\n\n- Tuan thu luat an toan\n- Quan ly state tot",
      sources: ["log#ev_01", "codebase/ai.py:15"]
    };
  }

  async ledgerSave(taskId: string, summary: string, details?: string): Promise<OkResult> {
    this.ledgerItems.unshift({
      id: `ledger_${Date.now()}`,
      timestamp: new Date().toISOString(),
      task_id: taskId,
      summary,
      details
    });
    return { status: "ok" };
  }

  async ledgerList(): Promise<LedgerListResult> {
    return { items: this.ledgerItems };
  }
}

interface LedgerItemModel {
  id: string;
  timestamp: string;
  task_id: string;
  summary: string;
  details?: string;
}
