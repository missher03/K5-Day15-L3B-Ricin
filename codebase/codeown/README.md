# codeown — lõi Python (phần A: Monitor)

Chỉ dùng thư viện chuẩn, Python 3.10+. Hợp đồng dữ liệu và lệnh: `task.md` mục 0.

## Chạy thử nhanh
```bash
python -m unittest discover -s tests -v                        # 38 test phần A
python codebase/codeown_cli.py init --repo <repo-của-bạn>        # ghi hook Claude Code + git post-commit + .gitignore
python codebase/codeown_cli.py status --repo <repo>              # chữ dễ đọc: task, DI, số dòng AI / người, nhắc
python codebase/codeown_cli.py status --repo <repo> --json       # một dòng JSON cho extension
python codebase/codeown_cli.py log --repo <repo>                 # các sự kiện đã ghi (thêm --jsonl: mỗi sự kiện một dòng)
python codebase/codeown_cli.py attribute --repo <repo>           # từng dòng code kèm nhãn AI / AI* / người (--jsonl: mỗi dòng một bản ghi)
python codebase/codeown_cli.py task new --repo <repo> --name login   # bắt đầu task mới (diff tính từ HEAD hiện tại)
```
Trong thư mục `codebase/` thì `python -m codeown <lệnh>` tương đương.
Eval: `{"mode": "monitor", "session_id": "demo01"}` → `agent.answer()` đọc `data/samples/sessions/demo01/`.

## Dữ liệu trong `.codeown/` (đều là JSONL: mỗi dòng một bản ghi, chỉ ghi thêm)
`events.jsonl` sự kiện · `summary.jsonl` một dòng mỗi commit (DI, số dòng) · `labels.jsonl` nhãn prompt · `state.jsonl`, `config.jsonl` (dòng sau đè dòng trước). Riêng `.claude/settings.json` phải là JSON vì Claude Code đọc nó.

## File
| File | Việc |
|---|---|
| `events.py` | ghi / đọc `.codeown/events.jsonl`, che bí mật, hash dòng, task_id |
| `hook.py` | `codeown hook --tool=claude_code|cursor|git` đọc JSON stdin → 1 sự kiện. Lỗi luôn bị nuốt |
| `install.py` | `codeown init`: gộp hook vào `.claude/settings.json`, `.cursor/hooks.json`, `post-commit`; chạy lại không nhân đôi |
| `attribution.py` | bỏ qua file không phải code của task (`DEFAULT_IGNORE`: file `init` sinh ra, lockfile, docs…; chỉnh bằng `{"ignore": [...]}` / `{"unignore": [...]}` trong `.codeown/config.jsonl`), rồi gán `ai_giu_nguyen` (trùng hash) / `ai_da_sua` (giống ≥0,6 cùng file, ≥0,8 khác file) / `nguoi_viet` |
| `classifier.py` | AI 1: luật regex (`--rules-only`) hoặc gọi model qua `ai.call_model`, lỗi thì lùi về luật |
| `dependence.py` | f1–f5 và DI theo `docs/design.md` §5.1 |
| `nudge.py` | 4 luật nhắc, tối đa 1 lần / 15 phút |
| `monitor.py` | ghép lại: `status`, `attribution_report`, `write_summary`, `analyze_offline` (cho eval) |
| `pretty.py` | in chữ dễ đọc cho CLI |

## Ghi chú cho B / C / D
- B: `monitor.attribution_report(repo, task_id)["lines"]` cho Examiner biết dòng nào `ai_giu_nguyen`. Lệnh `check`, `reflect`, `ledger`, `done` đang trả `{"error": "chưa làm (phần B: …)"}` (mã thoát 3) trong `__main__.py`, điền vào đó.
- C: phiên mẫu cho câu thử monitor để ở `data/samples/sessions/<id>/events.jsonl` (+ `diff.patch` tuỳ chọn). Câu thử có thể nhét thẳng `"events"` và `"patch"` vào input. Có `"now"` để cố định thời điểm khi thử luật nhắc.
- D: **luôn truyền `--json`**: `python <repo>/codebase/codeown_cli.py status --repo <workspace> --json` mỗi 10 giây; `pending_nudge` khác null thì hiện toast. Đã ghi sự kiện nudge nên lần gọi sau không lặp lại.
- Giới hạn đã biết: dòng AI ghi lưu chữ trong `meta.lines` (chỉ ở máy người dùng) để so độ giống; prompt được che bí mật và cắt 1000 ký tự; Copilot / Codex chưa có hook (CP4).
