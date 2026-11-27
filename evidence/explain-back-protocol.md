# Quy trình thử nghiệm "Giải thích lại" — 5–8 Junior (đo hành vi thật)

> Theo `docs/design.md` §2.3, `task.md` mục D và `eval/import_real_cases.py`.
> Đây là **bằng chứng mạnh nhất** (đo hành vi thật thay vì tự khai), đồng thời tạo **≥10 câu trả lời thật** để C nạp vào bộ câu thử Grader (`eval/benchmark.csv`) **trước lượt eval 1**.

---

## 1. Cách chọn đoạn code (ghi cố định TRƯỚC khi làm để không bị thiên vị)

- **Đối tượng:** 5–8 bạn lập trình viên ≤2 năm kinh nghiệm **ngoài nhóm** (đặt mã `E1`, `E2`, …, `E8`; không ghi tên).
- **Nguồn code:** 1 PR / commit / bài tập **gần nhất** (trong 2 tuần qua) mà bạn đó có dùng AI viết code.
- **Quy tắc chọn đúng 3 đoạn / người (mỗi đoạn ≤12 dòng):**
  1. Mở diff hoặc file chính có code AI viết (bỏ qua file config, lockfile, CSS/format thuần).
  2. Chọn **3 đoạn** có logic thật (ưu tiên: xử lý lỗi `try/catch/if`, truy vấn DB/API, xác thực/bảo mật, hoặc hàm xử lý dữ liệu chính), **không chọn trước dựa trên việc đoán người đó không biết**.
  3. Không cho bạn đó mở AI hay Google lúc trả lời; giải thích bằng lời tự nhiên, không biết thì nói thẳng "không biết".

---

## 2. Bộ câu hỏi cho từng đoạn code (lặp lại cho 3 đoạn / người)

| Bước | Câu hỏi chuẩn |
|---|---|
| 1 | *(Mở đúng đoạn code ≤12 dòng)* **"Đoạn này đang làm gì? Nếu bỏ hẳn (hoặc đổi điều kiện X thành Y) thì chuyện gì xảy ra?"** |
| 2 *(nếu trả lời mơ hồ)* | **"Bạn giải thích rõ hơn dòng [số dòng] vì sao phải viết như vậy thay vì cách đơn giản hơn không?"** |
| 3 *(hỏi ngắn sau 3 đoạn)* | **"Trước lúc mình hỏi, bạn có nghĩ mình đã hiểu hết cả 3 đoạn này không?"** *(để so tự tin chủ quan vs thực tế)* |

---

## 3. Cách chấm (2 người chấm độc lập rồi thống nhất nhãn)

Mỗi đoạn code gán 1 trong 4 nhãn khớp `eval/import_real_cases.py`:
- `hieu`: nêu đúng cơ chế **và** đúng hệ quả khi bỏ / đổi X.
- `mot_phan`: nói đúng ý chung nhưng thiếu cơ chế chính hoặc thiếu 1 vế.
- `chua_hieu`: giải thích sai cơ chế, nói chung chung không bám code, hoặc chỉ đọc lại tên biến/hàm.
- `khong_cham`: trả lời *"không biết"* hoặc quá ngắn (<15 ký tự).

**Chỉ số báo cáo vào `evidence/summary.md`:**
- Số đoạn giải thích đúng: **`x / N` đoạn** (`hieu` trên tổng `N = số người × 3` đoạn).
- Số người giải thích được hết cả 3 đoạn vs không giải thích được ít nhất 1 đoạn: **`x / n` người** *(n = 5–8 nên ghi `x/n`, không ghi %)*.

---

## 4. Cần lưu lại những gì? (2 nơi)

1. **Tóm tắt bằng chứng (commit được):** ghi kết quả tổng (`x/N` đoạn, `x/n` người, 2–3 trích dẫn đã bỏ tên) vào `evidence/summary.md`. **Không commit** code công ty hay log gốc của người thử.
2. **Dữ liệu câu thử thật cho C (`eval/real_cases.csv` — làm TRƯỚC lượt eval 1):**
   Chép `eval/real_cases_template.csv` thành `eval/real_cases.csv`, mỗi đoạn là 1 dòng, điền đủ **10 cột**:
   - `thay_cho`: `G01` … `G11` (id câu Grader sẽ được thay trong `eval/benchmark.csv`)
   - `nguon`: `E1`, `E2`… (**không ghi tên**)
   - `doan_code`: ≤12 dòng code đã **xoá tên công ty, tên dự án, key, email**
   - `cau_hoi`: nguyên câu đã hỏi ("Đoạn này làm gì, đổi X thì sao?")
   - `rubric`: ý đúng cần có (người chấm viết)
   - `cau_tra_loi`: lời người thử trả lời (bỏ tên, viết gọn nhưng **giữ nguyên ý và chỗ sai**)
   - `nhan`: `hieu` | `mot_phan` | `chua_hieu` | `khong_cham`
   - `khai_niem_hong`: **bắt buộc** khi `nhan` là `mot_phan` hoặc `chua_hieu`
   - `nguoi_cham`: 2 mã người chấm đã thống nhất, vd `A,D`
   - `kho`: `1` nếu là ca khó (đúng từ khoá nhưng sai cơ chế / đúng một nửa), không thì `0`

   Sau khi điền xong, chạy `python eval/import_real_cases.py` để kiểm tra (script tự quét email/SĐT/API key) rồi mới `--write`.
