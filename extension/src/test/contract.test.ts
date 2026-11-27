import assert from "node:assert/strict";
import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";
import test from "node:test";
import { readLatestPendingCheck, readLocalFallbackLedger } from "../client/localFallback";
import { MockCodeOwnClient } from "../client/mockClient";

test("MockCodeOwnClient dung hop dong va luong Check 2 vong", async () => {
  const client = new MockCodeOwnClient();

  const initRes = await client.init("/tmp/repo");
  assert.ok(initRes.hooks_written.length > 0);
  assert.equal(initRes.gitignore_updated, true);

  const statusRes = await client.status();
  assert.equal(statusRes.task_id, "t_20261127_01");
  assert.equal(statusRes.di, 64);
  assert.ok(statusRes.pending_nudge);
  assert.ok(statusRes.pending_check);

  const ackRes = await client.ackNudge(statusRes.pending_nudge.id ?? "ndg_01", "reply", "Thieu session");
  assert.equal(ackRes.ok, true);
  const afterAck = await client.status();
  assert.equal(afterAck.pending_nudge, null);

  const startRes = await client.checkStart(statusRes.task_id);
  assert.ok("questions" in startRes);
  assert.equal(startRes.questions.length, 3);

  const r1 = await client.checkAnswer(statusRes.task_id, "q1", "no bao loi");
  assert.equal(r1.label, "mot_phan");
  assert.equal(r1.round, 1);
  assert.equal(r1.final, false);
  assert.ok(r1.follow_up);

  const r2 = await client.checkAnswer(statusRes.task_id, "q1", "db.delete(None) nem loi dong 43, tra 500");
  assert.equal(r2.label, "hieu");
  assert.equal(r2.round, 2);
  assert.equal(r2.final, true);

  const reflectRes = await client.reflect(statusRes.task_id);
  assert.ok(reflectRes.markdown.includes("[log#ev_01]"));
  assert.ok(reflectRes.sources.length >= 2);

  const saveRes = await client.ledgerSave(statusRes.task_id, reflectRes.markdown);
  assert.equal(saveRes.ok, true);

  const listRes = await client.ledgerList();
  assert.ok(listRes.items.length >= 4);
  assert.ok(listRes.recent_nudges.length >= 2);
});

test("readLocalFallbackLedger doc dung ledger.jsonl va events.jsonl", () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "codeown-test-"));
  try {
    const codeownDir = path.join(tmpDir, ".codeown");
    fs.mkdirSync(codeownDir);

    fs.writeFileSync(
      path.join(codeownDir, "ledger.jsonl"),
      JSON.stringify({
        ts: "2026-11-27T10:00:00Z",
        task_id: "t_99",
        concept: "SQL injection",
        label: "chua_hieu",
        next_step: "Xem parameterized query"
      }) + "\n",
      "utf8"
    );

    fs.writeFileSync(
      path.join(codeownDir, "events.jsonl"),
      JSON.stringify({
        ts: "2026-11-27T09:50:00Z",
        event: "nudge",
        meta: { rule: "same_error_3x", summary: "Dan loi 3 lan", action: "reply" }
      }) + "\n",
      "utf8"
    );

    fs.writeFileSync(
      path.join(codeownDir, "summary.jsonl"),
      JSON.stringify({
        ts: "2026-11-27T10:05:00Z",
        task_id: "t_99",
        commit: "abcdef1234",
        di: 64,
        stats: { ai_giu_nguyen: 25, ai_da_sua: 5, nguoi_viet: 4 }
      }) + "\n",
      "utf8"
    );

    const res = readLocalFallbackLedger(tmpDir);
    assert.equal(res.items.length, 1);
    assert.equal(res.items[0].concept, "SQL injection");
    assert.equal(res.items[0].label, "chua_hieu");
    assert.equal(res.recent_nudges.length, 1);
    assert.equal(res.recent_nudges[0].action, "reply");

    const pc = readLatestPendingCheck(tmpDir);
    assert.ok(pc);
    assert.equal(pc.commit, "abcdef1234");
    assert.equal(pc.question_count, 3);
  } finally {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }
});
