import {
  CheckAnswerResult,
  CheckStartResult,
  InitResult,
  LedgerListResult,
  OkResult,
  ReflectResult,
  StatusResult
} from "../types";

// Giao dien chung cho CliCodeOwnClient va MockCodeOwnClient
export interface ICodeOwnClient {
  init(repoPath: string, rulesOnly?: boolean): Promise<InitResult>;
  status(): Promise<StatusResult>;
  ackNudge(nudgeId: string, action: "reply" | "dismiss", replyText?: string): Promise<OkResult>;
  checkStart(taskId: string): Promise<CheckStartResult>;
  checkAnswer(taskId: string, qid: string, text: string): Promise<CheckAnswerResult>;
  reflect(taskId: string): Promise<ReflectResult>;
  ledgerSave(taskId: string, markdown?: string): Promise<OkResult>;
  ledgerList(): Promise<LedgerListResult>;
}
