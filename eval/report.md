# Báo cáo đánh giá — lượt 1 → một cải tiến → lượt 2

> Điền ở guide bước 4.1. Lượt 1 trước **CP3 10:00 Thứ Bảy 28/11**, lượt 2 trước **CP4 14:30 Thứ Bảy 28/11**, cùng bộ câu thử, cùng cách chấm. Chấm ở rubric R5.
> Số lấy từ `python run.py score eval/run-1.csv` (và `run-2.csv`) sau khi điền cột `pass`. **Kết quả thấp ghi thật vẫn đủ điểm.**
> Không được: sửa chuẩn "đạt", bỏ câu thử trượt, sửa `expected` cho khớp output, sửa kết quả lượt đã chạy.

## 1. Kết quả

| Lượt | Run ID | Đạt / tổng | % | thuong | kho | tu_choi | So với chuẩn "đạt" |
|---|---|---|---|---|---|---|---|
| 1 | `run-4@20261127-192716` | 25/28 | 89% | 15/17 | 7/8 | 3/3 | **đạt** (≥75% câu qua; `cham_khop_nguoi` 89% ≥80% · `bo_sot_chua_hieu` 0% ≤10% · `khong_lo_dap_an` 100% · `tu_choi_dung` 100%) |
| 2 | `run-5@20261128-103708` | 27/28 | 96% | 16/17 | 8/8 | 3/3 | **đạt** (≥75% câu qua; `cham_khop_nguoi` 89% ≥80% · `bo_sot_chua_hieu` 0% ≤10% · `khong_lo_dap_an` 100% · `tu_choi_dung` 100%) |

Kết quả từng câu: lượt 1 = `eval/run-4.csv` (bảng metric: `eval/auto-score-run-4.md`), lượt 2 = `eval/run-5.csv` (`eval/auto-score-run-5.md`). Trace: `traces/run-4.jsonl`, `traces/run-5.jsonl`. Cột `pass` lượt 2 theo đề xuất `auto_score`; người xem lại G06, G10, M05 và giữ nguyên đề xuất.

Vì sao lượt 1 là `run-4`: đây là lượt đầu chạy đúng cấu hình cố định ở `eval/README.md` §4 (Claude Haiku 5.5 + Sonnet 5.5, giám khảo thứ hai bật) trên code đã gộp đủ A/B/C/D (`main` 27/11). `run-1`, `run-2` (Groq gpt-oss) và `run-3` (Claude, trước khi gộp xong) là lượt nối model, ghi ở `spec.md` §10, không tính. `run-3` cùng model ra đúng 25/28 với đúng 3 câu trượt như `run-4` → kết quả ổn định giữa hai lần chạy.

Lượt 2 chạy 28/11 10:37, cùng cấu hình §4 của `eval/README.md`, cùng 28 câu, 0 lỗi kỹ thuật (`python run.py eval` → `auto_score --fill --md` → `python run.py score eval/run-5.csv`).

Token lượt 1: vào 64.907 · ra 10.965 · tổng thời gian 111,6 giây cho 28 câu. Lượt 2: vào 62.371 · ra 10.085 · 99,4 giây (trung bình 1,1 lần gọi model mỗi câu).

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
- Trạng thái kiểm (trước lượt 2, chỉ chạy với AI giả, không gọi model):
  - **G06 — đã sửa, đã kiểm offline:** câu trả lời dán code → `need_own_words`, không gọi model; thêm test `test_pasted_code_without_diff_asks_for_own_words`.
  - **M05 — đã sửa, đã kiểm offline:** `examine repo07_c1` → `skip: diff chỉ đổi định dạng / tên`; trong 12 repo mẫu chỉ repo07 (định dạng) và repo12 (docs) bị bỏ qua; thêm 2 test.
  - **G10 — đã sửa prompt, CHƯA kiểm:** chỉ biết được khi chạy lượt 2 với model thật; có thể làm đổi nhãn ở G02 / G04 / G08 / G09 (các câu đáp án `chua_hieu`).
- Kết quả: nhóm lỗi đó (G06) 0/1 → **1/1** · tổng 89% → **96%** (25/28 → 27/28; thuong 15/17 → 16/17 · kho 7/8 → 8/8 · tu_choi 3/3 → 3/3).
  - **G06:** lượt 2 trả `need_own_words`, không chấm, gợi ý yêu cầu giải thích bằng lời → đạt.
  - **M05:** lượt 2 trả `skip: diff chỉ đổi định dạng / tên`, không câu hỏi nào → đạt.
  - **G10: vẫn trượt.** Lượt 2 vẫn chấm `chua_hieu` (0,8), giống hệt lượt 1; sửa prompt chưa đủ để đổi nhãn ca biên này. Vẫn tính là câu trượt, không bỏ.
- Câu nào **tệ đi** sau khi sửa: **không có.** So từng câu run-4 → run-5: chỉ G06 và M05 đổi kết quả (0 → 1); nhãn của 10 câu Grader còn lại (gồm G02, G04, G08, G09 đáp án `chua_hieu`) giữ nguyên, `bo_sot_chua_hieu` vẫn 0/4. 6/6 metric vẫn đạt.

## 4. Còn lại

- Lỗi chưa sửa + nguy hiểm thế nào: (1) G10 vẫn trượt ở lượt 2 — Grader chấm ca biên thấp hơn người chấm (`chua_hieu` thay vì `mot_phan`). Lỗi này về phía khắt khe: người dùng bị hỏi lại / thấy "chưa hiểu" dù đã chạm đúng ý, gây bực và mất thời gian, nhưng không làm sót người chưa hiểu (`bo_sot_chua_hieu` vẫn 0%). Từ bản extension 28/11, người dùng có nút "Sang câu tiếp theo" nên không bị kẹt. (2) Bộ câu thử 0/28 từ người dùng thật — số 89% mới đo trên ca nhóm viết và ca sinh từ seed; thử "giải thích lại" mới có 2 người (`evidence/summary.md`). (3) Luật "trông như code" của G06 dựa vào dấu câu / từ khoá, có thể bắt nhầm câu giải thích viết bằng tiếng Anh nhiều dấu code.
- Nếu có thêm 1 tuần: thay ≥10 câu Grader bằng câu giải thích thật của junior (đúng quy trình: code AI viết cho chính họ) · chạy lượt 3 trên bộ câu mới, thêm vài ca biên giống G10 để sửa riêng ranh giới `mot_phan` / `chua_hieu` · đo thử toàn Haiku để giảm chi phí ~10 lần nếu giữ được `bo_sot_chua_hieu` ≤10% · thử Check ≤2 phút vì "mất thời gian" là lý do không dùng số 1 (khảo sát 10/17).
