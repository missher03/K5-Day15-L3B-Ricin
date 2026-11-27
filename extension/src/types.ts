export type GradeLabel = "hieu" | "mot_phan" | "chua_hieu";

export interface LineStats {
  total: number;
  covered: number;
  uncovered: number;
  di: number; // Deficit Index 0-100
}

export interface PendingNudge {
  id: string;
  commit_sha: string;
  file: string;
  line: number;
  question: string;
  timestamp: string;
}

export interface PendingCheck {
  commit_sha: string;
  files: string[];
  reason: string;
}

export interface StatusResult {
  enabled: boolean;
  repo: string;
  commit: string;
  line_stats: LineStats;
  pending_nudge: PendingNudge | null;
  pending_check: PendingCheck | null;
}

export interface InitResult {
  status: string;
  repo: string;
  rules_only?: boolean;
}

export interface CheckQuestion {
  question_id: string;
  file: string;
  start_line: number;
  end_line: number;
  question: string;
  context_hint?: string;
}

export interface CheckStartResult {
  session_id: string;
  commit_sha: string;
  questions: CheckQuestion[];
}

export interface CheckAnswerResult {
  grade: GradeLabel;
  feedback: string;
  missing_concept?: string;
  hint?: string;
  round: number;
}

export interface ReflectResult {
  reflect_markdown: string;
  sources: string[];
}

export interface LedgerItem {
  id: string;
  timestamp: string;
  task_id: string;
  summary: string;
  details?: string;
}

export interface NudgeHistoryItem {
  id: string;
  timestamp: string;
  file: string;
  line: number;
  question: string;
  ack_type: "reply" | "dismiss";
  reply_text?: string;
}

export interface LedgerListResult {
  items: LedgerItem[];
}

export interface OkResult {
  status: string;
  [key: string]: any;
}
