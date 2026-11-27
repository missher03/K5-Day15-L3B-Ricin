# Data card — dữ liệu bản chạy thử CodeOwn dùng

> Nhóm Ricin · phần C (Lê Thành Nguyên). Bản đầu CP2, đủ ở CP3.
> **Mọi dữ liệu trong `data/` hiện là tự dựng (`synthetic`), không phải bằng chứng pain.** Bằng chứng pain nằm ở `evidence/` (phần D).
> Không dùng: code công ty, log thật của người khác, file `.env` của bất kỳ project nào, dữ liệu BTC cấp.
> Sinh lại toàn bộ: `python data/samples/build_samples.py` (seed 42, chỉ thư viện chuẩn, chạy lại ra đúng từng byte). Kiểm mà không ghi: thêm `--check`.

## Dataset 1 · Repo mẫu + diff "AI viết" (`data/samples/repo01…repo12`)

| | |
|---|---|
| Dùng để làm gì | Đầu vào cho Examiner (`mode: examine`), Reflect (`mode: reflect`), gán dòng của A, simulate (`mode: task`); công cụ `read_diff`, `read_file`, `run_snippet` |
| Từ đâu | Nhóm tự viết tay trong `build_samples.py` (biến `REPOS`): 9 Python, 3 JS / Markdown — CRUD Flask, đọc CSV Excel, đăng nhập hash mật khẩu, fetch có timeout / retry, upload file, search SQL, debounce, cache TTL, thanh toán idempotency, middleware JWT, 1 diff chỉ đổi định dạng, 1 diff chỉ đổi docs / config |
| Xử lý những bước gì | Mỗi dòng code được gắn tay một trong 4 vai: không đổi · AI viết giữ nguyên · AI viết rồi người sửa (kèm bản AI gốc) · người viết. Script sinh `diff.patch` (một hunk / file), `events.jsonl` (prompt, `ai_edit` kèm sha1 các dòng AI, `ai_bash`, `ai_turn_end`, `commit`), `truth.json` |
| Số dòng / số đoạn | 12 repo · 190 dòng thêm có nhãn: 172 `ai_giu_nguyen` · 5 `ai_da_sua` · 13 `nguoi_viet` (dòng trống / chỉ ngoặc không tính) |
| Phiên bản / ngày lấy | Sinh 27/11/2026, seed 42 |
| Nhãn | `synthetic` |
| Giới hạn | Repo nhỏ (5–35 dòng thêm / repo), mỗi repo 1 commit; tỉ lệ `ai_da_sua` thấp hơn thật (người sửa ít dòng); chưa có TypeScript / Java; prompt do nhóm viết, không phải prompt thật |

## Dataset 2 · Phiên log sinh tự động (`data/samples/sessions/sess01…sess40`)

| | |
|---|---|
| Dùng để làm gì | Monitor (`mode: monitor`): kiểm DI, f1–f5, luật nhắc của A; 5 phiên đầu là bộ kiểm DI (`fixtures/di_sessions.json`, sai lệch cho phép ±5) |
| Từ đâu | `build_samples.py` sinh từ 3 kiểu dùng: `tu_luc` (ít AI, tự viết test) · `can_bang` · `phu_thuoc` (dán lỗi nhiều, nhận gần hết code AI, commit nhanh). Tỉ lệ kiểu ở phiên 6–40: 0,3 / 0,4 / 0,3 *(tự ước tính, chưa lấy từ phỏng vấn)* |
| Xử lý những bước gì | Dòng code sinh từ mẫu câu có tên biến ngẫu nhiên; dòng "người sửa" = dòng AI đổi 1 tên / số; dòng người viết được lấy lại tới khi SequenceMatcher < 0,6 với mọi dòng AI. Phiên 1–5 ép kịch bản: DI cao · tự lực · cân bằng · dán cùng lỗi 3 lần · nhận 58 dòng một lần |
| Số dòng / số đoạn | 40 phiên · 1.730 dòng có nhãn (1.070 `ai_giu_nguyen` · 334 `ai_da_sua` · 326 `nguoi_viet`) · DI từ 9 đến 72 (trung vị 36; 3 phiên > 70; 24 phiên < 40) |
| Phiên bản / ngày lấy | Sinh 27/11/2026, seed 42 |
| Nhãn | `synthetic` |
| Giới hạn | Code sinh từ mẫu câu nên không chạy được, chỉ để gán dòng / DI; không có sự kiện "người sửa file" xen giữa các prompt, nên điều kiện "giữa hai prompt cùng lỗi không có dòng `nguoi_viet`" của f3 luôn đúng; kiểu dùng chưa kiểm với người thật |

**Đáp án (`truth.json`) tính thế nào** — đúng công thức `docs/design.md` §5.1, chạy được bằng code, không chấm tay:
- Nhãn dòng: theo vai đã gắn khi dựng. Script tự kiểm vai khớp đúng thuật toán của A (trùng hash → `ai_giu_nguyen`; ≥0,6 với một dòng AI → `ai_da_sua`; còn lại `nguoi_viet`; bỏ dòng trống / chỉ ngoặc) — vi phạm thì script dừng, không ghi.
- f1 = giữ nguyên / (giữ nguyên + đã sửa) · f2 = tỉ lệ prompt `lam_ho` + `debug_dan_loi` · f3 = số chuỗi ≥2 prompt liền nhau có dòng lỗi đầu tiên (regex `…Error|Exception…`) giống ≥0,8 · f4 = trung vị giây từ `ai_edit` tới commit · f5 = có dòng `nguoi_viet` trong file test. f3 chặn trên 5, f4 chặn trên 600 giây.
- DI = 100 × (0,3·f1 + 0,25·f2 + 0,2·f3ₙ + 0,15·(1−f4ₙ) + 0,1·(1−f5)), làm tròn.
- Luật nhắc: `lap_loi` (≥3 prompt liền cùng lỗi) · `nhan_nhieu_dong` (≥50 dòng `ai_edit` trong 30 giây) · `lam_ho_ca_tinh_nang` (prompt `lam_ho` cho cả tính năng — nhãn gắn tay) · `di_cao` (DI > 70); `nudges_fired` áp giới hạn 1 lần / 15 phút.
- Nhãn prompt (`prompt_labels`) gắn tay theo 5 nhãn Classifier.

## Dataset 3 · Fixture kiểm đơn vị cho A và B (`data/samples/fixtures/`)

| | |
|---|---|
| Dùng để làm gì | `classifier_prompts.json`: 20 prompt có nhãn (4 / nhãn) cho Classifier của A (mục tiêu ≥80%) · `guard_cases.json`: 8 ví dụ lộ / không lộ đáp án cho `guard.leaks_answer` của B · `di_sessions.json`: 5 phiên có DI kỳ vọng cho `dependence.compute` của A |
| Từ đâu | Nhóm tự viết |
| Nhãn | `synthetic` |
| Giới hạn | Nhỏ; prompt viết bởi người trong nhóm, có thể "sạch" hơn prompt thật |

## Dataset 4 · Câu trả lời trong bộ câu thử Grader (`eval/benchmark.csv`, G01–G11, T01–T03)

| | |
|---|---|
| Dùng để làm gì | Đầu vào cho Grader; nhãn người chấm ở `eval/bench_truth.json` |
| Từ đâu | **Hiện là nhóm tự viết** theo 3 mức (hiểu / một phần / chưa hiểu) + các ca khó (đúng từ khoá sai cơ chế, dán code, quá ngắn). Kế hoạch: thay ≥10 câu bằng câu giải thích thật từ thử nghiệm "giải thích lại" của D (bỏ tên, viết lại), đổi `source` thành `nguoi_dung: E<số>` |
| Nhãn | `tu_viet` (chưa có câu `nguoi_dung` nào — `python run.py check` đang cảnh báo 0/28) |
| Giới hạn | Nhãn người chấm hiện do 1 người (C) gắn, chưa có người thứ hai thống nhất |

## Dataset 5 · Docs offline (`data/docs/*.md`)

| | |
|---|---|
| Dùng để làm gì | Công cụ `search_docs` (Grader / Reflector trích `[docs:link]`, gợi ý khi từ chối) |
| Từ đâu | 11 trang tóm tắt **do nhóm tự viết lại** từ kiến thức chung, mỗi trang có `link:` tới docs gốc (Python docs, MDN, OWASP, jsonwebtoken, Stripe) |
| Xử lý | Không chép nguyên văn trang gốc |
| Nhãn | tự viết |
| Giới hạn | **Chưa đối chiếu từng câu với trang gốc** (ghi ở dòng `nguon:` từng file) — cần một người mở link kiểm trước CP3 |

## Dữ liệu `synthetic` — người kiểm

- Cách sinh: `data/samples/build_samples.py`, seed 42; script tự kiểm luật gán nhãn (0 vi phạm ở bản này).
- Người kiểm tay: **chưa có** — cần một người ngoài C đọc 2 repo mẫu + 2 phiên, đối chiếu `truth.json`, ghi số dòng đã kiểm vào đây.
