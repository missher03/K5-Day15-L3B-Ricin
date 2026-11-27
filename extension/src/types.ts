// Kieu du lieu khop hop dong task.md muc 0.3-0.6 va Contract Addendum

export type GradeLabel = "hieu" | "mot_phan" | "chua_hieu";

export interface LineStats {
  ai_giu_nguyen: number;
  ai_da_sua: number;
  nguoi_viet: number;
}

export interface PendingNudge {
  id?: string;
  event_id?: string | null;
  rule: string;
  message: string;
  metric_text?: string;
  ts: string;
}

export interface PendingCheck {
  task_id: string;
  commit: string;
  commit_msg: string;
  ai_lines: number;
  total_lines: number;
  question_count: number;
}

export interface StatusResult {
  task_id: string;
  task_title?: string;
  di: number | null;
  stats: LineStats;
  pending_nudge: PendingNudge | null;
  pending_check?: PendingCheck | null;
}

export interface InitResult {
  hooks_written: string[];
  gitignore_updated: boolean;
}

export interface CheckQuestion {
  qid: string;
  file: string;
  lines: [number, number];
  concept: string;
  question: string;
}

export interface CheckQuestionsPayload {
  task_id: string;
  questions: CheckQuestion[];
}

export interface CheckSkipPayload {
  skip: string;
}

export type CheckStartResult = CheckQuestionsPayload | CheckSkipPayload;

export interface CheckAnswerResult {
  qid: string;
  label: GradeLabel;
  confidence: number;
  missing_concept: string | null;
  hint: string;
  follow_up: string | null;
  round: number;
  final: boolean;
}

export interface ReflectResult {
  markdown: string;
  sources: string[];
}

export interface LedgerItem {
  ts: string;
  task_id: string;
  concept: string;
  label: GradeLabel;
  next_step?: string;
}

export interface NudgeHistoryItem {
  ts: string;
  rule: string;
  summary: string;
  action: "reply" | "dismiss";
}

export interface LedgerListResult {
  items: LedgerItem[];
  recent_nudges: NudgeHistoryItem[];
}

export interface OkResult {
  ok: boolean;
}
