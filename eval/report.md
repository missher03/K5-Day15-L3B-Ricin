# Báo cáo đánh giá — lượt 1 → một cải tiến → lượt 2

> Điền ở guide bước 4.1. Lượt 1 trước **CP3 10:00 Thứ Bảy 28/11**, lượt 2 trước **CP4 14:30 Thứ Bảy 28/11**, cùng bộ câu thử, cùng cách chấm. Chấm ở rubric R5.
> Số lấy từ `python run.py score eval/run-1.csv` (và `run-2.csv`) sau khi điền cột `pass`. **Kết quả thấp ghi thật vẫn đủ điểm.**
> Không được: sửa chuẩn "đạt", bỏ câu thử trượt, sửa `expected` cho khớp output, sửa kết quả lượt đã chạy.

## 1. Kết quả

| Lượt | Run ID | Đạt / tổng | % | thuong | kho | tu_choi | So với chuẩn "đạt" |
|---|---|---|---|---|---|---|---|
| 1 | `run-4@20261127-192716` | 25/28 | 89% | 15/17 | 7/8 | 3/3 | **đạt** (≥75% câu qua; `cham_khop_nguoi` 89% ≥80% · `bo_sot_chua_hieu` 0% ≤10% · `khong_lo_dap_an` 100% · `tu_choi_dung` 100%) |
| 2 | | __/__ | | __/__ | __/__ | __/__ | đạt / chưa |

Kết quả từng câu: lượt 1 = `eval/run-4.csv` (bảng metric: `eval/auto-score-run-4.md`), lượt 2 = run kế tiếp. Trace: `traces/run-4.jsonl`.

Vì sao lượt 1 là `run-4`: đây là lượt đầu chạy đúng cấu hình cố định ở `eval/README.md` §4 (Claude Haiku 5.5 + Sonnet 5.5, giám khảo thứ hai bật) trên code đã gộp đủ A/B/C/D (`main` 27/11). `run-1`, `run-2` (Groq gpt-oss) và `run-3` (Claude, trước khi gộp xong) là lượt nối model, ghi ở `spec.md` §10, không tính. `run-3` cùng model ra đúng 25/28 với đúng 3 câu trượt như `run-4` → kết quả ổn định giữa hai lần chạy.

Token lượt 1: vào 64.907 · ra 10.965 · tổng thời gian 111,6 giây cho 28 câu.

## 2. Lỗi lượt 1 — gom thành nhóm có tên

| Nhóm lỗi | Số câu | Câu |
|---|---|---|
| Không nhận ra câu trả lời là code dán lại → vẫn chấm | 1 | G06 |
| Mở Check cho diff chỉ đổi định dạng / tên biến | 1 | M05 |
| Chấm khắt khe ở ranh giới `mot_phan` / `chua_hieu` | 1 | G10 |

**≥3 lỗi cụ thể:**

| Câu | Input | Output | Vì sao sai |
|---|---|---|---|
| G06 (kho) | Hỏi `auth.py:26` kiểm điều kiện gì; người dùng trả lời bằng nguyên 2 dòng code `if count >= MAX_ATTEMPTS and ...` / `raise PermissionError(...)` | `status: graded`, nhãn `mot_phan` (0,6) | Lẽ ra `need_own_words`, không chấm. Luật "dán code" (`grader.is_pasted`) chỉ so với `diff_codes`; câu thử không gửi kèm `diff` nên luật không chạy và model chấm code như câu giải thích |
| M05 (thuong) | `examine repo07_c1`: diff chỉ đổi định dạng + tên biến `s` → `text` | Mở Check, 3 câu hỏi về regex / thứ tự `lower()` / `strip("-")` | Lẽ ra `skip`. `examiner.should_open` chỉ nhận `lines` (dòng thêm), không có dòng bị xoá nên không so được dáng code cũ / mới; luật này chỉ có ở nhánh giả `agent.fake_examine` |
| G10 (thuong) | Vòng 2: bỏ `{ algorithms: ["HS256"] }` thì kẻ tấn công gửi token thế nào; trả lời "jwt không biết dùng thuật toán nào để kiểm, chắc sẽ lỗi" | Nhãn `chua_hieu` (0,8), `final: true` | Người chấm: `mot_phan` vì đã chạm đúng thành phần (thuật toán kiểm chữ ký) dù kết luận sai. Prompt Grader bảo "không chắc giữa hai nhãn thì chọn nhãn thấp hơn" nên đẩy ca biên xuống `chua_hieu` |

## 3. Một lần cải tiến

- Nhắm vào nhóm lỗi: **không nhận ra câu trả lời là code dán lại (G06)** — vì sao là nhóm **đau nhất với người dùng**: junior dán lại code mà vẫn được chấm `mot_phan` nghĩa là CodeOwn chấm cả việc chép, đúng pain "nộp được nhưng không giải thích được"; kịch bản này đã ghi ở `spec.md` §5.
- Đã sửa gì (có thể vài thay đổi cùng nhắm nhóm lỗi đó): `grader.is_pasted` — khi không có diff thì đếm dòng trông như code (bỏ chuỗi trong nháy, không có chữ tiếng Việt có dấu, mở đầu bằng từ khoá hoặc kết thúc bằng `: ; { } ( )`); ≥2 dòng và ≥80% dòng như vậy → `need_own_words`, không gọi model. Sửa kèm (cùng lượt 2, ghi riêng để không lẫn): M05 — `examiner.should_open` nhận thêm dòng bị xoá, cùng dáng code (bỏ khoảng trắng, thay tên bằng `x`) → `skip: diff chỉ đổi định dạng / tên`; G10 — prompt Grader: phân vân `mot_phan` / `chua_hieu` mà câu trả lời đã chỉ đúng phần code quyết định → `mot_phan`. Kiểm offline (AI giả): G06 → `need_own_words`, M05 → `skip`; 11 câu grade / từ chối còn lại không bị luật mới bắt nhầm. G10 phải chờ lượt 2 với model thật.
- Kết quả: nhóm lỗi đó __/__ → __/__ · tổng __% → __%
- Câu nào **tệ đi** sau khi sửa: __

## 4. Còn lại

- Lỗi chưa sửa + nguy hiểm thế nào: __
- Nếu có thêm 1 tuần: __
