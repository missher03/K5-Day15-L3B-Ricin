import test from "node:test";
import assert from "node:assert";
import * as fs from "fs";
import * as path from "path";
import { MockCodeOwnClient } from "../client/mockClient";
import { readLocalFallbackLedger } from "../client/localFallback";

test("MockCodeOwnClient full flow test", async () => {
  const client = new MockCodeOwnClient();

  const initRes = await client.init();
  assert.equal(initRes.status, "ok");

  const statusRes = await client.status();
  assert.equal(statusRes.enabled, true);
  assert.equal(statusRes.repo, "vin-ai-lab");
  assert.ok(statusRes.line_stats);

  const ackRes = await client.ackNudge("ev_01", "reply", "Giai thich thu nghiem");
  assert.equal(ackRes.status, "ok");

  const checkStart = await client.checkStart();
  assert.equal(checkStart.session_id, "mock_session_123");
  assert.ok(checkStart.questions.length > 0);

  const q = checkStart.questions[0];
  const ansRes = await client.checkAnswer(checkStart.session_id, q.question_id, "Cau tra loi dung ban chat");
  assert.equal(ansRes.grade, "hieu");

  const reflectRes = await client.reflect();
  assert.ok(reflectRes.reflect_markdown.length > 0);
  assert.ok(reflectRes.sources.length > 0);

  const saveRes = await client.ledgerSave("task_test", "Test summary", "Test details");
  assert.equal(saveRes.status, "ok");

  const listRes = await client.ledgerList();
  assert.ok(listRes.items.length > 0);
});

test("Local fallback ledger reading test", async () => {
  const tmpDir = fs.mkdtempSync(path.join(process.cwd(), "tmp-test-"));
  const codeownDir = path.join(tmpDir, ".codeown");
  fs.mkdirSync(codeownDir);

  const ledgerPath = path.join(codeownDir, "ledger.jsonl");
  const testItem = {
    id: "item_99",
    timestamp: "2026-11-27T10:00:00Z",
    task_id: "task_99",
    summary: "Fallback ledger test item"
  };
  fs.writeFileSync(ledgerPath, JSON.stringify(testItem) + "\n");

  const result = readLocalFallbackLedger(tmpDir);
  assert.equal(result.items.length, 1);
  assert.equal(result.items[0].summary, "Fallback ledger test item");
  assert.equal(result.items[0].task_id, "task_99");

  // Cleanup
  fs.rmSync(tmpDir, { recursive: true, force: true });
});
