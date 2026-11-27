import { spawn } from "child_process";
import * as vscode from "vscode";
import { buildProcessEnv, getApiKey } from "../secrets";
import {
  CheckAnswerResult,
  CheckStartResult,
  InitResult,
  LedgerListResult,
  OkResult,
  ReflectResult,
  StatusResult
} from "../types";
import { ICodeOwnClient } from "./interface";
import { readLocalFallbackLedger } from "./localFallback";

// Goi loi Python qua python -m codeown <lenh> --json
export class CliCodeOwnClient implements ICodeOwnClient {
  constructor(private context: vscode.ExtensionContext, private workspaceRoot: string) {}

  private async runPython<T>(args: string[], timeoutMs = 10000, stdinData?: string): Promise<T> {
    const apiKey = await getApiKey(this.context);
    const { pythonPath, env } = buildProcessEnv(this.workspaceRoot, apiKey);

    return new Promise<T>((resolve, reject) => {
      const child = spawn(pythonPath, ["-m", "codeown", ...args], {
        cwd: this.workspaceRoot,
        env
      });

      let stdout = "";
      let stderr = "";
      let timedOut = false;

      const timer = setTimeout(() => {
        timedOut = true;
        child.kill();
        reject(new Error(`Lệnh CodeOwn quá thời gian (${timeoutMs / 1000}s).`));
      }, timeoutMs);

      if (stdinData !== undefined && child.stdin) {
        child.stdin.write(stdinData, "utf8");
        child.stdin.end();
      }

      child.stdout.on("data", (chunk: Buffer) => {
        stdout += chunk.toString("utf8");
      });

      child.stderr.on("data", (chunk: Buffer) => {
        stderr += chunk.toString("utf8");
      });

      child.on("error", (err) => {
        clearTimeout(timer);
        reject(new Error(`Không chạy được ${pythonPath}: ${err.message}`));
      });

      child.on("close", (code) => {
        clearTimeout(timer);
        if (timedOut) {
          return;
        }
        const parsed = this.parseJsonOutput(stdout);
        if (code !== 0) {
          const errMsg = parsed && typeof parsed === "object" && "error" in parsed
            ? String((parsed as { error: unknown }).error)
            : (stderr.trim() || stdout.trim() || `Mã thoát ${code}`);
          reject(new Error(errMsg));
          return;
        }
        if (parsed === null) {
          reject(new Error(`CLI trả dữ liệu không hợp lệ: ${stdout.slice(0, 120)}`));
          return;
        }
        resolve(parsed as T);
      });
    });
  }

  private parseJsonOutput(raw: string): unknown {
    const trimmed = raw.trim();
    if (!trimmed) {
      return null;
    }
    try {
      return JSON.parse(trimmed);
    } catch {
      const lines = trimmed.split("\n").reverse();
      for (const line of lines) {
        try {
          return JSON.parse(line);
        } catch {
          // Thu dong truoc do
        }
      }
      return null;
    }
  }

  init(repoPath: string, rulesOnly?: boolean): Promise<InitResult> {
    const args = ["init", "--repo", repoPath];
    if (rulesOnly) {
      args.push("--rules-only");
    }
    return this.runPython<InitResult>(args, 10000);
  }

  status(): Promise<StatusResult> {
    return this.runPython<StatusResult>(["status", "--json"], 5000);
  }

  ackNudge(nudgeId: string, action: "reply" | "dismiss", replyText?: string): Promise<OkResult> {
    const args = ["nudge", "ack", "--id", nudgeId, "--action", action];
    if (replyText) {
      args.push("--text", replyText);
    }
    args.push("--json");
    return this.runPython<OkResult>(args, 5000);
  }

  checkStart(taskId: string): Promise<CheckStartResult> {
    return this.runPython<CheckStartResult>(["check", "start", "--task", taskId, "--json"], 30000);
  }

  checkAnswer(taskId: string, qid: string, text: string): Promise<CheckAnswerResult> {
    return this.runPython<CheckAnswerResult>(
      ["check", "answer", "--task", taskId, "--qid", qid, "--text", text, "--json"],
      30000
    );
  }

  reflect(taskId: string): Promise<ReflectResult> {
    return this.runPython<ReflectResult>(["reflect", "--task", taskId, "--json"], 30000);
  }

  ledgerSave(taskId: string, markdown?: string): Promise<OkResult> {
    const args = ["ledger", "save", "--task", taskId];
    if (markdown !== undefined) {
      args.push("--from-stdin");
    }
    args.push("--json");
    return this.runPython<OkResult>(args, 10000, markdown);
  }

  async ledgerList(): Promise<LedgerListResult> {
    try {
      return await this.runPython<LedgerListResult>(["ledger", "list", "--json"], 5000);
    } catch {
      return readLocalFallbackLedger(this.workspaceRoot);
    }
  }
}
