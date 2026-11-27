# Trích dẫn công khai & Nguồn số liệu Impact

> Theo yêu cầu bằng chứng Pain & Impact (`spec.md` §1–§2, `docs/design.md` §2.3–§2.4).
> **Luật:** không bịa số, không bịa trích dẫn. Số nào chưa tìm được nguồn công khai thì ghi rõ *(tự ước tính)*. Trích dẫn công khai **tối đa 2 câu, bỏ tên người đăng**, bắt buộc kèm **link gốc + ngày xem**.

---

## 1. Năm trích dẫn công khai (Reddit · Voz · nhóm dev Facebook)

*Chủ đề: lập trình viên mới / junior phụ thuộc AI viết code, nộp bài/PR nhưng không hiểu hoặc không tự debug được.*

| # | Kênh | Trích dẫn nguyên văn (≤2 câu, bỏ tên) | Link bài / bình luận | Ngày xem |
|---|---|---|---|---|
| 1 | Reddit (`r/ExperiencedDevs` / `r/cscareerquestions`…) | "…" | https://... | 27/11/2026 |
| 2 | Voz (chuyên mục IT / Phần mềm) | "…" | https://... | 27/11/2026 |
| 3 | Nhóm dev Facebook (bỏ tên người đăng) | "…" | https://... | 27/11/2026 |
| 4 | | "…" | https://... | 27/11/2026 |
| 5 | | "…" | https://... | 27/11/2026 |

---

## 2. Bảng số liệu cho phần Impact (`spec.md` §2)

Công thức: **Impact / tháng = số người bị ảnh hưởng × số lần / tháng × giờ mất mỗi lần.**

| Hạng mục số | Giá trị thu được | Nguồn cụ thể (hoặc ghi *tự ước tính*) | Link / file + ngày xem |
|---|---|---|---|
| **Số lập trình viên mới (≤2 năm KN) ở Việt Nam** | ____ người | Báo cáo công khai (vd: TopDev *Vietnam IT Market Report* hoặc ITviec *Salary & IT Market Report* — lấy tổng số lập trình viên VN × tỉ lệ ≤2 năm KN, ghi rõ số trang/mục) | Link: ____ · xem __/__/2026 |
| **Tỉ lệ không giải thích được code AI đã nộp** | ____% (hoặc `x/n`) | Khảo sát câu **B4** (và kiểm chéo bằng thử nghiệm "giải thích lại" `x/n` người) | `evidence/survey/results.csv` + `evidence/summary.md` |
| **Số lần dùng AI / task dùng AI mỗi tuần** | ____ lần / tuần | Khảo sát câu **B1** (số task dùng AI tuần qua; câu **A3** là tần suất dùng; câu **B6** là số lần dán lỗi tuần qua) | `evidence/survey/results.csv` |
| **Số lần PR bị trả lại / bị hỏi không trả lời được / tháng** | ____ lần / tháng | Khảo sát câu **B5, B7** + phỏng vấn `P1`–`P4` | `evidence/summary.md` |
| **Thời gian 1 senior mất để review lại** | ____ giờ / tuần (≈ ____ phút / lần) | Phỏng vấn senior **`P4.md`** (kiểm chéo bằng khảo sát Phần D câu D2–D3 nếu có) | `evidence/interviews/P4.md` |
| **Thời gian 1 junior tự gỡ khi kẹt** | ____ phút / lần | Khảo sát câu **B8** + phỏng vấn `P1`–`P3` | `evidence/summary.md` |
