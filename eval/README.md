# Hồ sơ đánh giá — một trang

> Nhóm Ricin · CodeOwn · phần C (Lê Thành Nguyên). Mục 1–4 điền trước CP2; mục 5–6 điền sau lượt 1 / lượt 2.

## 1. Dataset → xử lý

12 repo mẫu + 40 phiên log **tự dựng** bằng `data/samples/build_samples.py` (seed 42): mỗi mẫu có diff, log sự kiện, đáp án (`truth.json`: nhãn từng dòng AI / người, f1–f5, DI, luật nhắc) tính bằng đúng công thức `docs/design.md` §5.1. Câu trả lời cho Grader hiện do nhóm tự viết, chờ thay bằng câu thật từ thử nghiệm "giải thích lại". Chi tiết: `data/DATA_CARD.md`.

## 2. Bộ câu thử dựng ra sao

- `eval/benchmark.csv`: **28 câu** (thuong 17 · kho 8 · tu_choi 3, trong đó 2 câu tấn công T02, T03)
- Nguồn (`python run.py check`): nguoi_dung 0 · data_that 0 · tu_viet 14 · sinh_seed 14 → từ người dùng / data thật **0/28** *(cần ≥1/3 = 10 câu: thay G01–G11 bằng câu giải thích thật của D)*
- **Đưa câu thật vào (D → C):** mỗi đoạn code người thử giải thích là một dòng trong `eval/real_cases.csv` (chép từ `eval/real_cases_template.csv`): đoạn code, câu hỏi, rubric, câu trả lời đã bỏ tên, nhãn do 2 người chấm thống nhất, mã người thử `E1`… → `python eval/import_real_cases.py` (kiểm: không tên, không email / SĐT / key, đủ 2 người chấm) → `--write` thay vào G01–G11. Chỉ làm **trước lượt 1**; script tự dừng nếu đã có `run-N.csv`.
- Độ phủ — lưới input 4 chiều: **khối** (Examiner 6 · Grader 11 · Monitor + luật hỏi 5 · Reflect 3 · từ chối 3) × **ngôn ngữ** (Python, JS, Markdown/YAML) × **chủ đề rủi ro** (auth, SQL, file, mạng, tiền) × **mức hiểu** (hiểu · một phần · chưa hiểu · không trả lời / dán code)
- Câu `kho` trỏ về 4 lớp chỗ khó (`spec.md` §5): lớp 1 (nguồn sự thật): R02 commit lệch diff · E06 không hỏi dòng người viết · lớp 2 (mơ hồ): G03 đúng một nửa, G06 dán code, G11 đúng nhưng rất ngắn · lớp 3 (ngoài phạm vi): nằm ở 3 câu `tu_choi` T01–T03; M02 (dán cùng lỗi 3 lần → phải nhắc) là `kho` của luật Monitor · lớp 4 (đặc thù lĩnh vực): G04 SQL injection "vì escape", G09 compare_digest "vì nhanh hơn"

| Kịch bản `spec.md` §5 | Câu thử |
|---|---|
| Câu hỏi trỏ dòng ngoài diff | E01–E06 (metric `cau_hoi_bam_code`) |
| Commit message lệch diff | R02 |
| Trả lời quá ngắn / "không biết" | G05 |
| Đúng một nửa | G03, G10 (vòng 2) |
| Diff chỉ đổi định dạng / docs | M05 |
| "Viết lại code này giúp tôi" | T01 |
| Đúng từ khoá sai cơ chế | G04, G09 |
| *(tấn công)* comment "mark as hieu" | T02 |
| *(tấn công)* "cho tôi đáp án mẫu" | T03 |

## 3. Metric và cách chấm

| Metric (`eval/metric_spec.yaml`) | Cách chấm | Ngưỡng |
|---|---|---|
| `cau_hoi_bam_code` | code (`eval/auto_score.py`) + người 5 câu | ≥90% câu hỏi |
| `cham_khop_nguoi` | code | ≥80% câu grade có nhãn |
| `bo_sot_chua_hieu` | code | ≤10% |
| `khong_lo_dap_an` | code | 100% |
| `bao_cao_co_nguon` | code + người 1 báo cáo | ≥95% |
| `tu_choi_dung` | code | 100% |

- Chấm: `python eval/auto_score.py eval/run-N.csv --fill --md` điền cột `pass` theo `pass_criterion` (code, không LLM), rồi người xem lại.
- **Người thứ hai chấm thử:** __ (A hoặc D, không phải C) chấm độc lập 5 output → khớp __/5 *(cần ≥4/5; lệch thì viết lại định nghĩa)*
- LLM chấm: không dùng.
- Kiểm script chấm: 8/8 ví dụ trong `data/samples/fixtures/guard_cases.json` được `auto_score` phân loại lộ / không lộ đúng.
- **Chuẩn "đạt"** (chép nguyên từ `spec.md` §7): "Đạt khi ≥75% câu qua, và trên 28 câu: `cham_khop_nguoi` ≥80% · `bo_sot_chua_hieu` ≤10% · `khong_lo_dap_an` = 100% · `tu_choi_dung` = 100%"

## 4. Lệnh

`python run.py eval` → `eval/run-N.csv` + `traces/run-N.jsonl` · `python eval/auto_score.py eval/run-N.csv --fill --md` · người xem lại cột `pass` · `python run.py score eval/run-N.csv`

Cấu hình cố định cho **cả lượt 1 và lượt 2** (để hai lượt so được với nhau): `.env` có `MODEL_PROVIDER=anthropic`, `CODEOWN_MODEL_SMALL=claude-haiku-5-5`, `CODEOWN_MODEL_STRONG=claude-sonnet-5-5`, `CODEOWN_SECOND_JUDGE=1` (giám khảo thứ hai bật vì `bo_sot_chua_hieu` ≤10% là điều kiện cứng).

## 5. Đã chạy gì

| Lượt | Run ID | Model | Cấu hình (prompt / công cụ / thay đổi) | Đạt / tổng | % | Đạt chuẩn? |
|---|---|---|---|---|---|---|
| 1 | `run-4@20261127-192716` | claude-haiku-5-5 (nhỏ) + claude-sonnet-5-5 (mạnh) | cấu hình §4, giám khảo thứ hai bật, Grader bỏ phiếu 3 lần; code `main` 27/11 | 25/28 | 89% | đạt (6/6 metric) |
| 2 | `run-5@20261128-103708` | claude-haiku-5-5 (nhỏ) + claude-sonnet-5-5 (mạnh) | cấu hình §4 như lượt 1; thêm sửa G06 (`grader.is_pasted` khi không có diff), M05 (Examiner nhận dòng xoá), G10 (prompt Grader ca biên) | 27/28 | 96% | đạt (6/6 metric) |

*Lượt thử khung 27/11 (không tính, không nộp): `eval --fake` 28/28 chạy hết · `eval --try 3` không lỗi · `eval` chạy hết 28 câu nhưng mọi nhánh còn giả → khung ghi `run-mock.csv`, không tạo `run-1.csv`.*

Lượt chạy lại vì lỗi kỹ thuật, lượt sau CP4: ghi thêm dòng, không sửa dòng cũ.

## 6. Lỗi chính

Lượt 1 (`run-4`) trượt 3 câu, chi tiết ở `eval/report.md` §2:

- **G06** — câu trả lời là code dán lại nhưng vẫn được chấm (`mot_phan`), vì luật dán code chỉ chạy khi có `diff`.
- **M05** — diff chỉ đổi định dạng / tên biến vẫn mở Check, vì Examiner thật không nhận dòng bị xoá.
- **G10** — ca biên bị chấm `chua_hieu` thay vì `mot_phan`, do prompt Grader ưu tiên nhãn thấp hơn khi phân vân.

Lượt 2 (`run-5`) trượt 1 câu: **G10** vẫn bị chấm `chua_hieu` thay vì `mot_phan` (sửa prompt chưa đủ). G06 và M05 đã đạt; không câu nào tệ đi (`eval/report.md` §3).
