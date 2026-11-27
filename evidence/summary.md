# Tổng hợp bằng chứng pain

> Điền ở guide bước 1.2, xong trước **CP3 10:00 Thứ Bảy 28/11**. Chấm ở rubric R1.
> Ba nguồn ngang nhau — tối thiểu **≥1 nguồn đạt ngưỡng**. Mạnh nhất: đào data ra insight → hỏi người dùng để kiểm lại (hoặc ngược lại).

## 1. Nguồn đã dùng

| Nguồn | Đạt ngưỡng? | File |
|---|---|---|
| Đào data (x/N, %, cách đếm chạy lại được, ≥5 ví dụ) | ☐ | `evidence/data-mining.md` |
| Phỏng vấn (≥3 người ngoài nhóm, đúng người dùng) | ☐ | `evidence/interviews/P1.md`… |
| Khảo sát (≥20 người ngoài nhóm, đúng người dùng) | ◐ **chưa đủ**: 20 phiếu nhưng 3 là senior → 17 phiếu đúng người dùng (<20) | `evidence/survey/results.csv`, `evidence/survey/count.py` |

## 2. Số chính

> Khảo sát: số dưới đây in từ `python evidence/survey/count.py evidence/survey/results.csv` (chạy lại được) và khớp số đếm tay của nhóm. `results.csv` đã bỏ cột thời gian và cột liên hệ (câu 17).

- Đào data: __/__ (__%) …
- Phỏng vấn: __/3 người gặp *(n nhỏ không ghi %)* · số lần / tháng: P1 __, P2 __, P3 __ · mỗi lần mất __–__ phút
- Khảo sát (form 18 câu, phát 27/11/2026, **mẫu thuận tiện**, N = 20 = 17 người dùng đích + 3 senior, đếm riêng):

| Chỉ số | Cả mẫu (n=20) | Không phải senior (n=17) | Senior (n=3) |
|---|---|---|---|
| Dùng AI khi code mỗi ngày | 19/20 (95%) | 16/17 (94%) | 3/3 |
| ≥6/10 lần dùng luôn code AI không sửa | 9/20 (45%) | 8/17 (47%) | 1/3 |
| 30 ngày qua từng nhờ AI làm hộ cả tính năng / bài tập | 17/20 (85%) | 15/17 (88%) | 2/3 |
| Tự tin giải thích ≤50% code AI viết gần nhất | 12/20 (60%) | 12/17 (71%) | 0/3 |
| **30 ngày qua từng không giải thích được code mình nộp khi bị hỏi** | **16/20 (80%)** | **15/17 (88%)** | 1/3 |
| — trong đó hơn 3 lần | 6/20 (30%) | 6/17 (35%) | 0/3 |
| Đổi yêu cầu một chút thì không tự sửa được code AI | 17/20 (85%) | 16/17 (94%) | 1/3 |
| Từng bị review trả lại / trừ điểm / hỏi khó vì code AI không hiểu | 10/20 (50%) | 10/17 (59%) | 0/3 |
| Lo phụ thuộc AI ≥4/5 | 12/20 (60%) | 12/17 (71%) | 0/3 |
| Sẽ dùng công cụ: chắc chắn có / có thể / không | 6 / 14 / 0 trên 20 | 5 / 12 / 0 trên 17 | 1 / 2 / 0 |
| Chấp nhận mỗi lần trả lời: <2 / 2–5 / 5–10 phút | 8 / 7 / 5 trên 20 | 7 / 6 / 4 trên 17 | 1 / 1 / 1 |

  Điều cản dùng công cụ (không phải senior, chọn nhiều): mất thời gian 10/17 · sợ bị theo dõi 9/17 · phiền khi bị nhắc 5/17.

  **Giới hạn của số này:** (1) mẫu thuận tiện, không đại diện; (2) form đã phát **khác** form ghi trước ở `evidence/survey/questions.md`: không có câu B4 nên **chưa đo đúng ngưỡng đã đặt** ở `evidence/hypothesis.md` (≥40% chọn B4). Câu gần nhất là câu 9 ("không giải thích được code mình nộp khi bị hỏi"), dùng làm số thay thế và ghi rõ là thay thế; (3) câu 1 và câu 2 lệch: 4 người chọn "Fresher / junior (<2 năm)" nhưng câu 2 chọn ">2 năm code" (có thể tính cả thời gian học) — nhóm đích ở đây lấy theo câu 1; nếu lấy theo câu 2 (≤2 năm) thì chỉ còn n = 10, câu 9 = 9/10; (4) không hỏi số task / tháng nên `uses_per_month` vẫn là tự ước tính.

Phỏng vấn nhiều vai thì đếm theo từng vai, không cộng chung.

| | Vai | Gặp pain? | Số lần / 1 tháng qua | Lần gần nhất mất | Đang xoay xở bằng |
|---|---|---|---|---|---|
| P1 | | | | | |
| P2 | | | | | |
| P3 | | | | | |

## 3. ≥5 trích dẫn hoặc ví dụ nguyên văn (có nguồn, bỏ tên)

1. "Hôm đấy giao phó toàn bộ cho gehihi, đọc lướt mỗi đề nên khi bị hỏi lớ ngớ luôn." — phiếu khảo sát S07, câu 11b
2. *(còn thiếu — câu 11b và 18 chỉ có 1 câu kể chuyện thật; 1 câu khác là "không", 1 câu là lời chúc, không dùng. Bổ sung từ phỏng vấn P1–P4 / `evidence/public-quotes.md`.)*
3.
4.
5.

## 4. Các nguồn có khớp nhau không

Data nói __; người dùng nói __. Khớp / lệch ở đâu, vì sao: __

## 5. Kết luận

Giả thuyết ở `evidence/hypothesis.md`: **chưa kết luận được theo đúng ngưỡng đã đặt** (form không có câu B4). Số thay thế ủng hộ giả thuyết: 15/17 (88%) người dùng đích từng không giải thích được code mình nộp khi bị hỏi trong 30 ngày qua, 16/17 không tự sửa được khi đổi yêu cầu, 10/17 đã bị review trả lại / hỏi khó; 3 senior thì ít gặp hơn (1/3, 0/3). Điều vẫn chưa biết: tần suất / số giờ mất mỗi lần (form không hỏi), và khảo sát tự khai có khớp hành vi thật không → cần phỏng vấn P1–P4 và thử nghiệm "giải thích lại" để kiểm.

## Lịch hẹn (dùng cho CP2 — chỉ ghi vai và giờ, không tên)

| Vai | Giờ hẹn | Đã xong? |
|---|---|---|
| P1 · Junior dev / sinh viên IT (≤2 năm KN, dùng AI code) | 20:00–23:00 T6 27/11 | Chưa |
| P2 · Junior dev / sinh viên IT (≤2 năm KN, dùng AI code) | 20:00–23:00 T6 27/11 | Chưa |
| P3 · Junior dev / sinh viên IT (≤2 năm KN, dùng AI code) | 20:00–23:00 T6 27/11 | Chưa |
| P4 · Senior / tech lead (review PR của junior) | 20:00–23:00 T6 27/11 | Chưa |
| E1–E8 · 5–8 junior dev / sinh viên IT (thử nghiệm "giải thích lại") | 20:00–23:00 T6 27/11 | Chưa |
