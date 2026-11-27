# Báo cáo đánh giá — lượt 1 → một cải tiến → lượt 2

> Nhóm Ricin · CodeOwn · phần C (Lê Thành Nguyên) viết từ `eval/run-*.csv`, `eval/auto-score-run-*.md`, `spec.md` §10. Số lấy từ `python run.py score` sau khi điền cột `pass` bằng `eval/auto_score.py` (chấm bằng code theo `eval/metric_spec.yaml`).
> Cùng 28 câu, cùng cách chấm ở mọi lượt. Không sửa chuẩn "đạt", không bỏ câu trượt, không sửa `expected`, không sửa file lượt đã chạy.

## 1. Kết quả

| Lượt | File / Run ID | Model | Đạt / tổng | % | thuong | kho | tu_choi | So với chuẩn "đạt" |
|---|---|---|---|---|---|---|---|---|
| *(lỗi kỹ thuật)* | `run-1` · run-1@20261127-173949 | Groq gpt-oss-20b / 120b | 15/28 | 54% | 8/17 | 5/8 | 2/3 | không dùng: 10/28 câu lỗi HTTP 429 (hết hạn mức token / phút) → chạy lại thành `run-2` |
| **1** | `run-2` · run-2@20261127-174051 | Groq gpt-oss-20b / 120b | 21/28 | 75% | 14/17 | 4/8 | 3/3 | **chưa đạt**: `cham_khop_nguoi` 78% (<80%) |
| **2** | `run-3` · run-3@20261127-181857 | Claude Haiku 5.5 / Sonnet 5.5 | 25/28 | 89% | 15/17 | 7/8 | 3/3 | **đạt**: ≥75% câu qua và cả 6 metric qua ngưỡng |

Metric (code, `eval/auto-score-run-N.md`):

| Metric | Ngưỡng | Lượt 1 (`run-2`) | Lượt 2 (`run-3`) |
|---|---|---|---|
| `cau_hoi_bam_code` | ≥90% | 20/20 = 100% | 20/20 = 100% |
| `cham_khop_nguoi` | ≥80% | 7/9 = **78%** | 8/9 = 89% |
| `bo_sot_chua_hieu` | ≤10% | 0/4 = 0% | 0/4 = 0% |
| `khong_lo_dap_an` | 100% | 14/14 | 14/14 |
| `bao_cao_co_nguon` | ≥95% | 19/22 = **86%** | 28/28 = 100% |
| `tu_choi_dung` | 100% | 3/3 | 3/3 |

Kết quả từng câu: `eval/run-2.csv`, `eval/run-3.csv`. Trace: `traces/run-2.jsonl`, `traces/run-3.jsonl`.

**Đọc kết quả cho đúng:** giữa lượt 1 và lượt 2 nhóm đổi **cùng lúc** logic (Reflector, Grader bỏ phiếu) **và** model (Groq → Claude), vì Groq hết hạn mức ngày và đổi nhãn 21% giữa hai lần chấm (`spec.md` §10). Nên mức tăng 75% → 89% **không tách được** phần nào do sửa code, phần nào do model mạnh hơn. Bộ câu thử nhỏ (28 câu, 9 câu có nhãn Grader) nên 1 câu = 11 điểm % ở `cham_khop_nguoi`.

## 2. Lỗi lượt 1 — gom thành nhóm có tên

| Nhóm lỗi | Số câu | Câu |
|---|---|---|
| **Báo cáo Reflect có câu không nguồn / không gọi đúng chỗ lệch** | 3 | R01, R02, R03 |
| **Grader chấm nhẹ tay câu đúng từ khoá nhưng sai cơ chế bảo mật** (`chua_hieu` → `mot_phan`) | 2 | G04, G09 |
| **Luật tất định chạy trước model không bắt được ca** (dán code bị chấm `hieu`; diff chỉ đổi định dạng vẫn mở Check) | 2 | G06, M05 |

**≥3 lỗi cụ thể (lượt 1, `run-2`):**

| Câu | Input | Output | Vì sao sai |
|---|---|---|---|
| G04 | Hỏi vì sao dấu `?` chặn SQL injection; trả lời "thư viện sẽ escape các ký tự đặc biệt như dấu nháy" | `label: mot_phan`, hint "Bạn đã biết về việc escape chuỗi, nhưng còn một cách khác…" | Người chấm: `chua_hieu` — cơ chế đúng là tham số hoá (giá trị tách khỏi câu lệnh), không phải escape. Hint còn khẳng định cái sai là "đã biết" |
| G06 | Hỏi dòng `auth.py:26` kiểm gì; câu trả lời là **2 dòng code dán nguyên từ diff** | `label: hieu` | Luật thiết kế (§5.3): câu trả lời dán code → yêu cầu viết lại bằng lời, không chấm. Grader coi code dán là hiểu |
| M05 | `examine repo07_c1` — diff chỉ format PEP8 + đổi tên `s` → `text` | `skip: null`, 3 câu hỏi, vd "Vì sao trong hàm slugify, dòng 5 lại gọi `text = text.lower().strip()`?" | Luật mở Check: diff chỉ đổi định dạng / tên thì không hỏi. Hỏi ở đây làm người dùng thấy Check phiền và bấm bỏ qua |
| R02 | `reflect repo10_t1` — nhánh `fix/login`, commit "Sửa lỗi login" nhưng diff đổi `payment.py` | Mô tả đúng việc sửa `payment.py` (Decimal, idempotency key) và có câu "Có sự không khớp giữa nhánh fix/login, commit message … và prompt yêu cầu sửa hàm charge", nhưng 1/7 câu khẳng định có nguồn không hợp lệ | `bao_cao_co_nguon` 6/7 < 95%. Câu nêu lệch gọi "hàm charge" chứ không gọi tên việc (thanh toán) nên `auto_score` không tính — điểm này một phần do luật chấm của C chặt (đòi chữ "thanh toán / payment" trên cùng dòng); lỗi nguồn thì là lỗi thật |

## 3. Một lần cải tiến

- **Nhắm vào nhóm lỗi:** Reflect thiếu nguồn (B chọn, `spec.md` §10 lúc 18:00) — vì đây là nhóm trượt **cả 3/3 câu**, và báo cáo bịa lý do / không nguồn dạy sai cho junior đúng lúc họ định tự học lại (pain ở `docs/design.md` §1).
  *Ghi chú của C:* nhóm G04 / G09 nguy hiểm ngang — chấm nhẹ tay ca sai cơ chế bảo mật là đúng lỗi "tưởng đã hiểu" mà sản phẩm sinh ra để chặn. Lượt 1 vẫn giữ `bo_sot_chua_hieu` 0% (không câu nào bị chấm `hieu`) nên chưa vượt ngưỡng an toàn.
- **Đã sửa gì** (`spec.md` §10, B13 + Grader):
  - Reflector: phần câu hỏi cho người dùng thành tiêu đề riêng (không bị đếm là khẳng định không nguồn); chỉ gọi "lệch" khi hai nguồn nêu hai việc cụ thể khác nhau, nguồn mơ hồ → "chưa rõ" + hỏi lại.
  - Grader: bỏ phiếu đa số tới 3 lần; ranh giới `mot_phan` = có ít nhất một ý đúng của rubric.
  - Đổi model Groq → Claude Haiku 5.5 / Sonnet 5.5 (cùng lúc, xem mục 1).
- **Kết quả:** nhóm Reflect 0/3 → **3/3** · nhóm Grader sai cơ chế 0/2 → 2/2 · nhóm luật tất định 0/2 → 0/2 · tổng **75% → 89%** · `bao_cao_co_nguon` 86% → 100% · `cham_khop_nguoi` 78% → 89%
- **Câu tệ đi sau khi sửa:** **G10** (đạt → trượt) — câu hỏi vòng 2 về `algorithms: ["HS256"]`, câu trả lời "jwt không biết dùng thuật toán nào để kiểm, chắc sẽ lỗi": người chấm gắn `mot_phan`, lượt 2 chấm `chua_hieu`. Đây là ca biên; ranh giới mới "có ít nhất một ý đúng của rubric" làm Grader khắt khe hơn với câu nói đúng hướng nhưng không nêu ý rubric.

## 4. Còn lại

- **M05 — Check mở cho diff chỉ đổi định dạng / tên** (trượt cả 2 lượt): luật này ở `docs/design.md` §5.3 nhưng Examiner chưa cài. Nguy hiểm: người dùng bị hỏi vô lý sau mỗi lần format code → tắt CodeOwn. Sửa rẻ: so "dáng" dòng thêm / dòng xoá bằng code trước khi gọi Examiner (nhánh giả của `agent.py` đã có hàm `_shape` làm việc này).
- **G06 — câu trả lời dán code** (trượt cả 2 lượt; lượt 2 chấm `mot_phan` thay vì `hieu`, đỡ hơn nhưng vẫn chấm): luật "trùng ≥80% với diff → yêu cầu viết bằng lời" cần diff, mà câu thử `grade` không mang `diff_id`. Đây vừa là lỗi luật, vừa là giới hạn của câu thử (C) — không sửa input sau khi đã chạy; ghi lại để bộ câu thử bản sau có `diff_id`.
- **G10 — nhãn biên `mot_phan` / `chua_hieu`**: cần người chấm thứ hai xem lại nhãn người chấm của câu này trước khi coi là lỗi Grader.
- **Giới hạn của chính bộ câu thử:** 0/28 câu từ người dùng thật (câu trả lời Grader do nhóm tự viết); nhãn Grader do 1 người gắn, chưa có người thứ hai thống nhất (`eval/README.md` mục 3); dữ liệu repo / log là tự dựng.
- **Nếu có thêm 1 tuần:** thay G01–G11 bằng câu giải thích thật (đường nhập đã có: `eval/import_real_cases.py`); 2 người chấm độc lập cả 11 câu Grader; chạy lại lượt 1 trên Claude với code trước B13 để tách tác động của sửa code và của đổi model; thêm 10–20 câu Grader để mỗi câu không còn bằng 11 điểm %.

## 5. So cấu hình model (không phải lượt cải tiến)

`run-4` (run-4@20261127-193252): **cùng code với lượt 2**, chỉ đổi `CODEOWN_MODEL_STRONG` sang Haiku → toàn Claude Haiku 5.5. Mục đích: có tỉ lệ đạt thật cho cấu hình rẻ để tính chi phí / task thành công (`cost/cost-estimate.md`), theo gợi ý `docs/design.md` §9.2. Không dùng làm lượt cải tiến.

| | Lượt 2 `run-3` (Haiku + Sonnet) | `run-4` (toàn Haiku) |
|---|---|---|
| Đạt / tổng | 25/28 (89%) | 24/28 (86%) — **vẫn đạt chuẩn** |
| thuong / kho / tu_choi | 15/17 · 7/8 · 3/3 | 14/17 · 7/8 · 3/3 |
| `cham_khop_nguoi` · `bo_sot_chua_hieu` | 89% · 0% | 89% · 0% |
| `bao_cao_co_nguon` | 28/28 = 100% | 28/29 = 97% |
| Câu trượt | G06, G10, M05 | G06, G10, M05, **R03** (1 câu Reflect thiếu nguồn) |
| Token / câu (vào · ra) | 2.259 · 400 | 2.260 · 684 |

→ Đổi Examiner + Reflector từ Sonnet sang Haiku chỉ mất 1 câu (R03, phần Reflect do model mạnh làm), các metric an toàn (`bo_sot_chua_hieu`, `khong_lo_dap_an`, `tu_choi_dung`) giữ nguyên. 28 câu là nhỏ: chênh 1 câu chưa đủ kết luận hai cấu hình khác nhau thật.
