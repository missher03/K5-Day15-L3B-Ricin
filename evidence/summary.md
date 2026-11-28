# Tổng hợp bằng chứng pain

> Điền ở guide bước 1.2, xong trước **CP3 10:00 Thứ Bảy 28/11**. Chấm ở rubric R1.
> Ba nguồn ngang nhau — tối thiểu **≥1 nguồn đạt ngưỡng**. Mạnh nhất: đào data ra insight → hỏi người dùng để kiểm lại (hoặc ngược lại).

## 1. Nguồn đã dùng

| Nguồn | Đạt ngưỡng? | File |
|---|---|---|
| Đào data (x/N, %, cách đếm chạy lại được, ≥5 ví dụ) | ☐ | `evidence/data-mining.md` |
| Phỏng vấn (≥3 người ngoài nhóm, đúng người dùng) | ◐ **đủ số người, chưa chắc đúng người dùng**: 3 junior / fresher + 1 senior, nhưng 3 junior tự khai 3–3,5 năm code (>2 năm); phiếu chưa ghi ngày và chưa ghi có phải người ngoài nhóm | `evidence/interviews/phieu-phong-van.md` |
| Khảo sát (≥20 người ngoài nhóm, đúng người dùng) | ◐ **chưa đủ**: 20 phiếu nhưng 3 là senior → 17 phiếu đúng người dùng (<20) | `evidence/survey/results.csv`, `evidence/survey/count.py` |

## 2. Số chính

> Khảo sát: số dưới đây in từ `python evidence/survey/count.py evidence/survey/results.csv` (chạy lại được) và khớp số đếm tay của nhóm. `results.csv` đã bỏ cột thời gian và cột liên hệ (câu 17).

- Đào data: __/__ (__%) …
- Phỏng vấn (27/11, `evidence/interviews/phieu-phong-van.md`, n nhỏ nên chỉ ghi x/N): **junior 3/3** kể được một lần cụ thể đã nộp / commit code AI viết mà chưa hiểu hết · **2/3** sau đó bị hỏi mà không trả lời được (P1 khi demo trước lớp, P3 khi phỏng vấn xin việc) · 3/3 khi đổi yêu cầu hay gặp lỗi thì bảo AI làm lại · thời gian gỡ: P1 hơn 60 phút, P2 120–180 phút, P3 "nhiều thời gian" (không có số) · số lần / tháng: không hỏi được số (P1, P2, P3 đều để trống) · sẽ dùng công cụ: chắc chắn có 0/3, có thể 2/3, không 1/3; 2/3 nêu lo tốn thời gian. **Senior 1/1** xác nhận junior không giải thích được code AI viết "khá nhiều lần" và mình mất "khá nhiều thời gian" review, nhưng **không cho số** PR hay số phút.
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
| P1 | Junior · 3,5 năm code · Codex | Có (lab 14, phần deploy) | không có số | hơn 1 tiếng để sửa sau demo | bảo AI làm lại theo đề mới |
| P2 | Fresher · 3 năm · Gemini | Có (mini hackathon, AI code toàn bộ) | không có số | khoảng 2–3 tiếng sửa lỗi khi test | bảo AI viết lại rồi review |
| P3 | Fresher · 3 năm · Codex | Có (dự án cá nhân: RAG, monitoring, giao diện web) | "thỉnh thoảng" | "nhiều thời gian", không có số | mô tả lại cho AI, tự chạy test và review |
| S1 | Senior · 6 năm · Claude | Xác nhận từ phía reviewer | "khá nhiều lần" | "khá nhiều thời gian" | dùng AI rà code junior, hỏi câu chỉ người làm thật mới biết, chia sẻ cách dùng AI |

- Thử "giải thích lại" (28/11/2026, `evidence/interviews/phieu-giai-thich-lai.md`, **chỉ 2 người** ngoài nhóm E1, E2, mỗi người 3 đoạn = 6 đoạn; nhãn do nhóm chấm): hiểu 2/6 đoạn (E1b, E2a) · một phần 3/6 (E1a, E1c, E2b) · chưa hiểu 1/6 (E2c). Người có ít nhất 1 đoạn chưa giải thích đúng hoàn toàn: **2/2**. Lưu ý chấm: E2a được chấm "hiểu" dù câu 3 trả lời "để đọc tiếng Việt" (`utf-8-sig` là để bỏ BOM).

  **Đọc số này thận trọng:** (1) mẫu rất nhỏ, chưa đạt mốc 5–8 người của `hypothesis.md` và chưa đạt ≥10 câu thử thật cho benchmark

## 3. ≥5 trích dẫn hoặc ví dụ nguyên văn (có nguồn, bỏ tên)

1. "Hôm đấy giao phó toàn bộ cho gehihi, đọc lướt mỗi đề nên khi bị hỏi lớ ngớ luôn." — phiếu khảo sát S07, câu 11b
2. "Sau đó lên demo thì có mấy câu bị các bạn trong lớp hỏi mà không trả lời được, về sửa mất hơn 1 tiếng" — phỏng vấn P1, câu 3
3. "Lần làm hackathon, vì không đủ thời gian nên tôi chủ yếu dùng AI để code toàn bộ và commit thay vì rà soát bắt lỗi nó" — phỏng vấn P2, câu 2
4. "tôi không trả lời được một số câu hỏi của người phỏng vấn về dự án của mình, mất nhiều thời gian để đọc hiểu và làm lại sau đó" — phỏng vấn P3, câu 3
5. "Tôi thường mô tả lại cho AI và bảo AI code, tôi chỉ chạy test và review" — phỏng vấn P3, câu 4
6. "đa số mọi người đều phụ thuộc AI quá nhiều hoặc không biết cách tối ưu câu trả lời của AI" — phỏng vấn S1 (senior), câu 1
7. Ngược chiều: "Không vì tốn thời gian" — phỏng vấn P2, khi hỏi có dùng công cụ không (khớp với khảo sát: "mất thời gian" là lý do cản số 1, 10/17)

## 4. Các nguồn có khớp nhau không

Khảo sát nói 15/17 người dùng đích từng không giải thích được code mình nộp khi bị hỏi và 16/17 không tự sửa được khi đổi yêu cầu; phỏng vấn nói 3/3 junior kể được một lần cụ thể, 2/3 đã bị hỏi mà không trả lời được, 3/3 đổi yêu cầu thì giao lại cho AI → **khớp**. Senior xác nhận từ phía người review nhưng chưa có số. Hai nguồn cũng khớp ở rào cản: "mất thời gian" là lý do số 1 trong khảo sát (10/17) và 2/3 junior phỏng vấn nêu đúng lý do này → Check phải ngắn (khảo sát: 7/17 chỉ chấp nhận <2 phút). Lệch / chưa chắc: 3 junior phỏng vấn tự khai 3–3,5 năm code, cao hơn mốc ≤2 năm của người dùng chính; chưa có số lần / tháng và số phút của senior.

## 5. Kết luận

Giả thuyết ở `evidence/hypothesis.md`: **chưa kết luận được theo đúng ngưỡng đã đặt** (form không có câu B4). Số thay thế ủng hộ giả thuyết: 15/17 (88%) người dùng đích từng không giải thích được code mình nộp khi bị hỏi trong 30 ngày qua, 16/17 không tự sửa được khi đổi yêu cầu, 10/17 đã bị review trả lại / hỏi khó; 3 senior thì ít gặp hơn (1/3, 0/3). Phỏng vấn kiểm lại: 3/3 junior kể được lần cụ thể (ngưỡng ≥2/3 ở `hypothesis.md`, nhưng phiếu không hỏi rõ lần đó có nằm trong 1 tháng qua không), senior 1/1 xác nhận nhưng không cho số. Điều vẫn chưa biết: tần suất / tháng (form và phỏng vấn đều chưa có số), và khảo sát tự khai có khớp hành vi thật không → cần phỏng vấn P1–P4 và thử nghiệm "giải thích lại" để kiểm.

## Lịch hẹn (dùng cho CP2 — chỉ ghi vai và giờ, không tên)

| Vai | Giờ hẹn | Đã xong? |
|---|---|---|
| P1 · Junior dev / sinh viên IT (≤2 năm KN, dùng AI code) | 20:00–23:00 T6 27/11 | | Xong |
| P2 · Junior dev / sinh viên IT (≤2 năm KN, dùng AI code) | 20:00–23:00 T6 27/11 | | Xong |
| P3 · Junior dev / sinh viên IT (≤2 năm KN, dùng AI code) | 20:00–23:00 T6 27/11 | | Xong |
| P4 · Senior / tech lead (review PR của junior) | 20:00–23:00 T6 27/11 | | Xong (mã S1) |
| E1–E8 · 5–8 junior dev / sinh viên IT (thử nghiệm "giải thích lại") | 20:00–23:00 T6 27/11 | Chưa |
