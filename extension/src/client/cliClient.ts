import * as vscode from "vscode";
import { spawn } from "child_process";
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
import { buildProcessEnv, getApiKey } from "../secrets";
import { readLocalFallbackLedger } from "./localFallback";

export class CliCodeOwnClient implements ICodeOwnClient {
  constructor(private context: vscode.ExtensionContext, private workspaceRoot: string) {}

  private async runPython(args: string[], timeoutMs: number = 10000, stdinData?: string): Promise<any> {
    const apiKey = await getApiKey(this.context);
    const env = buildProcessEnv(this.context, this.workspaceRoot, apiKey);
    const pythonExec = env["PYTHON_EXECUTABLE"] || "python3";

    return new Promise((resolve, reject) => {
      const child = spawn(pythonExec, ["-m", "codeown", ...args, "--json"], {
        cwd: this.workspaceRoot,
        env,
        timeout: timeoutMs
      });

      let stdout = "";
      let stderr = "";

      if (stdinData && child.stdin) {
        child.stdin.write(stdinData);
        child.stdin.end();
      }

      child.stdout.on("data", (data) => {
        stdout += data.toString();
      });

      child.stderr.on("data", (data) => {
        stderr += data.toString();
      });

      child.on("error", (err) => {
        reject(new Error(`Khong the chay Python CLI (${pythonExec}): ${err.message}`));
      });

      child.on("close", (code) => {
        if (code !== 0) {
          reject(new Error(`Python CLI loi (code ${code}): ${stderr || stdout || "Unknown error"}`));
          return;
        }
        try {
          // Find last line or valid JSON in stdout
          const lines = stdout.trim().split("\n");
          let jsonParsed: any = null;
          for (let i = lines.length - 1; i >= 0; i--) {
            try {
              jsonParsed = JSON.parse(lines[i]);
              break;
            } catch {
              // try next
            }
          }
          if (!jsonParsed) {
            jsonParsed = JSON.parse(stdout);
          }
          resolve(jsonParsed);
        } catch (e: any) {
          reject(new Error(`Khong the parse JSON tu CLI: ${e.message}. Output: ${stdout}`));
        }
      });
    });
  }

  async init(rulesOnly?: boolean): Promise<InitResult> {
    const args = ["init"];
    if (rulesOnly) {
      args.push("--rules-only");
    }
    return await this.runPython(args, 15000);
  }

  async status(): Promise<StatusResult> {
    return await this.runPython(["status"], 10000);
  }

  async ackNudge(nudgeId: string, action: "reply" | "dismiss", replyText?: string): Promise<OkResult> {
    const args = ["nudge", "ack", nudgeId, "--action", action];
    if (replyText) {
      args.push("--text", replyText);
    }
    return await this.runPython(args, 10000);
  }

  async checkStart(): Promise<CheckStartResult> {
    return await this.runPython(["check", "start"], 30000);
  }

  async checkAnswer(sessionId: string, questionId: string, answer: string): Promise<CheckAnswerResult> {
    return await this.runPython(["check", "answer", sessionId, "--qid", questionId, "--answer", answer], 30000);
  }

  async reflect(): Promise<ReflectResult> {
    return await this.runPython(["reflect"], 30000);
  }

  async ledgerSave(taskId: string, summary: string, details?: string): Promise<OkResult> {
    const payload = JSON.stringify({ task_id: taskId, summary, details: details || "" });
    return await this.runPython(["ledger", "save", "--task", taskId, "--from-stdin"], 15000, payload);
  }

  async ledgerList(): Promise<LedgerListResult> {
    try {
      return await this.runPython(["ledger", "list"], 10000);
    } catch {
      // Fallback to local fallback ledger if CLI ledger list fails
      return readLocalFallbackLedger(this.workspaceRoot);
    }
  }
}
