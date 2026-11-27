# data/samples — dữ liệu mẫu tự dựng (C → A, B)

Sinh lại: `python data/samples/build_samples.py` (seed 42). Mô tả, giới hạn: `data/DATA_CARD.md`.

| Mã | Ví dụ | Trỏ tới |
|---|---|---|
| `diff_id` | `repo03_c1`, `sess12_c1` | commit "AI viết" của mẫu |
| `task_id` | `repo03_t1`, `sess12_t1` | task (khớp trường `task_id` trong `events.jsonl`) |
| `session_id` | `sess12`, `s_repo03` | phiên |

Tra mã → thư mục: `index.json`. Mỗi thư mục mẫu có `events.jsonl` (hợp đồng task.md 0.2), `diff.patch`, `meta.json`, `truth.json`; repo mẫu có thêm `repo/` (file sau commit) và `sim_answers.json`.

## Lõi `codeown` chạy trên mẫu thế nào

`codebase/agent.py` gọi lõi qua `tools.core("<module>")`, đúng chữ ký ở task.md:

| Module (người viết) | agent.py gọi | Khi chạy eval |
|---|---|---|
| `attribution` (A) | `attribute(task_id)` | trong `read_diff` |
| `dependence` (A) | `compute(task_id)` | trong `compute_dependence` |
| `nudge` (A) | `check_nudge(task_id)` | `mode: monitor` |
| `events` (A) | `read_events(task_id)` | trong `get_events` |
| `examiner` (B) | `examine(diff_lines, di, task_intent, ledger)` | `mode: examine` — trả `{"skip": …}` nếu không mở Check |
| `grader` (B) | `grade(question, rubric, answer, round)` | `mode: grade` |
| `reflector` (B) | `reflect(task_id)` | `mode: reflect` |
| `ledger` (B) | `recent_understood(n)`, `append(entry)` | Examiner / `write_ledger` (chỉ khi người dùng bấm Lưu) |

**Quy ước duy nhất cần theo:** trước mỗi lần gọi theo `task_id`, `tools.py` đặt biến môi trường `CODEOWN_HOME` = thư mục mẫu. Lõi đọc `$CODEOWN_HOME/events.jsonl` và `$CODEOWN_HOME/diff.patch` (không có biến thì dùng `.codeown/` + `git diff` như khi dùng thật). Module nào chưa có, agent trả kết quả giả có `"fake": true`.

## Kiểm phần của mình

- A — gán dòng: so `attribute("repo0N_t1")["lines"]` với `truth.json["lines"]` (mục tiêu ≥90% trên repo01–03).
- A — DI: `fixtures/di_sessions.json` (sess01–05, sai lệch ≤5). Classifier: `fixtures/classifier_prompts.json` (≥80%).
- A — nhắc: `truth.json["nudge_rules"]` / `["nudges_fired"]`.
- B — `guard.leaks_answer`: `fixtures/guard_cases.json` (8 ca).
- Cả bộ: `python run.py eval` rồi `python eval/auto_score.py eval/run-N.csv`.

**Không đọc `truth.json` trong lõi hay agent** — đó là đáp án; `tools.read_file` chặn file này.
