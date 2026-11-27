import {
  InitResult,
  StatusResult,
  CheckStartResult,
  CheckAnswerResult,
  ReflectResult,
  LedgerListResult,
  OkResult
} from "../types";

export interface ICodeOwnClient {
  init(rulesOnly?: boolean): Promise<InitResult>;
  status(): Promise<StatusResult>;
  ackNudge(nudgeId: string, action: "reply" | "dismiss", replyText?: string): Promise<OkResult>;
  checkStart(): Promise<CheckStartResult>;
  checkAnswer(sessionId: string, questionId: string, answer: string): Promise<CheckAnswerResult>;
  reflect(): Promise<ReflectResult>;
  ledgerSave(taskId: string, summary: string, details?: string): Promise<OkResult>;
  ledgerList(): Promise<LedgerListResult>;
}
