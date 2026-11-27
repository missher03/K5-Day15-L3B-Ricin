# Tự đánh giá CodeOwn theo rubric hackathon (27/11/2026, 15:35)

> Chấm theo `03-rubric.md`, `README.md`, `tracks/track-f-other-lane.md`. Điểm là **ước tính nếu làm đúng kế hoạch trong `docs/design.md`**. Hiện tại mới có thiết kế: chưa có bằng chứng, chưa có code, repo chưa lên GitHub, nên nếu chấm ngay bây giờ thì gần như 0.

## Tổng quan

| Khối | Tối đa | Ước tính | Rủi ro chính |
|---|---:|---:|---|
| 4 checkpoint | 15 | 8–15 | CP1 còn 1,5 giờ, repo chưa push, chưa cho lab coach xem thẻ đề F |
| R1 Bằng chứng pain | 14 | 5–11 | Chưa có số nào; track F bị soi kỹ |
| R2 Impact | 11 | 5–8 | Hầu hết thừa số đang là *(tự ước tính)* |
| R3 Giải pháp AI | 16 | 10–14 | Thiết kế mạnh; extension VS Code dễ ăn hết giờ |
| R4 Bộ câu thử + metric | 14 | 8–12 | Khó có ≥1/3 câu nguồn thật; chuẩn "đạt" phải chốt trước 19:30 |
| R5 Báo cáo đánh giá | 8 | 5–7 | Cần đủ thời gian chạy lượt 2 |
| R6 Chi phí | 12 | 7–10 | Persona chưa có nguồn; simulate phải chạy thật |
| R7 Slide & demo | 10 | 6–8 | Mọi người phải trả lời được câu hỏi vặn |
| Bonus người dùng thử | +5 | 0–4 | Cần 2–3 junior dùng thử có log |
| **Tổng** | **100** | **~55–80** | Phụ thuộc gần hết vào tối nay |

## Điều kiện cứng (thiếu 1 là không xét giải)
1. Bản chạy thử gọi AI thật: **chưa có**. Khả thi nếu Check chạy bằng Python trước, extension sau.
2. Bằng chứng pain ≥1 nguồn đạt ngưỡng: **chưa có**. Phải phát khảo sát ngay.
3. Bộ câu thử ≥20 câu có % đạt: **chưa có**. Thiết kế 28 câu đã có.
4. `demo-slides.pdf`: **chưa có**.

## Từng khối

### Checkpoint (15)
- **CP1 17:00 (3):** cần `TEAMS.md` đủ người (hiện mới có tên nhóm, lớp, link), track F + bài toán không chữ AI, lát cắt, `canvas.md` + thẻ đề, **repo công khai mở được**. Repo hiện **trống trên GitHub** vì Claude chưa có quyền push → bạn tự push hoặc cấp quyền. Thẻ đề F phải đưa lab coach xem **trước** 17:00.
- **CP2 19:30 (4):** `spec.md` §4 có sơ đồ (có sẵn trong design), benchmark ≥10, `metric_spec.yaml`, `DATA_CARD.md`, **chuẩn "đạt" chốt và commit**, `run.py` chạy với AI giả. Làm được nếu bắt đầu ngay sau CP1.
- **CP3, CP4:** khả thi nếu tối nay nối model thật xong.

### R1 · Bằng chứng pain (14)
- **Mạnh:** kế hoạch 3 nguồn (khảo sát, phỏng vấn, thử nghiệm "giải thích lại"), câu hỏi hành vi chứ không hỏi ý kiến.
- **Yếu:** 0 số liệu. Track F phải có insight từ người dùng thật. Gom ≥20 junior **ngoài nhóm** trong một buổi tối là khó nhất của cả bài. Số liệu công khai (Stack Overflow…) không tính là nguồn đạt ngưỡng.
- **Để tối đa:** phát form ngay hôm nay qua nhóm lớp, nhóm dev, bạn bè đi làm IT; phỏng vấn 3 junior + 1 senior tối nay; thử nghiệm "giải thích lại" trên 5 người là nguồn thứ hai (+3 điểm). Ghi cách đếm trước khi đếm.

### R2 · Impact (11)
- **Mạnh:** có công thức, có bảng 4 hướng kèm lý do loại.
- **Yếu:** số lập trình viên mới ở VN, tỉ lệ bị ảnh hưởng, giờ mất mỗi lần đều chưa có nguồn.
- **Để tối đa:** lấy tỉ lệ và số lần từ khảo sát, giờ mất từ phỏng vấn senior, quy mô từ một báo cáo công khai có link. Thừa số nào chưa có nguồn thì ghi *(tự ước tính)*, không được bỏ trống.

### R3 · Giải pháp AI: thiết kế + bản chạy thử (16)
- **Mạnh:** lát cắt rõ (Check là quyết định trung tâm), workflow có lý do, bảng công cụ, chỗ người duyệt, chặn rủi ro lộ đáp án, ≥3 nguyên tắc có G10.
- **Yếu:** phạm vi lớn (hook nhiều công cụ + extension + 3 khối). Rubric không cho điểm riêng cho extension; điểm nằm ở chỗ **code khớp sơ đồ, gọi AI thật, người ngoài chạy được**.
- **Để tối đa:** làm theo thứ tự: (1) lõi Python `answer(text)` cho Check, gọi model thật; (2) Reflect; (3) Monitor tính DI từ log mẫu; (4) extension chỉ là lớp vỏ, làm nếu còn giờ. README phải có lệnh chạy. Phần còn giả ghi rõ.

### R4 · Bộ câu thử + metric (14)
- **Mạnh:** 28 câu chia theo khối, 6 metric kiểm được, có `bo_sot_chua_hieu` (lỗi nguy hiểm nhất), 2 câu tấn công.
- **Yếu:** **≥1/3 câu phải có nguồn từ người dùng / data thật**; câu giải thích tự viết không tính. Cần người thứ hai chấm 5 output khớp ≥4/5. Chuẩn "đạt" sửa sau 19:30 → R4 = 0.
- **Để tối đa:** lấy ≥10 câu giải thích thật từ thử nghiệm "giải thích lại" (đã bỏ tên); commit `metric_spec.yaml` + `spec.md` §7 trước 19:30; dùng ngưỡng thấp vừa phải, vì kết quả thấp mà thật vẫn đủ điểm.

### R5 · Báo cáo đánh giá (8)
- **Để tối đa:** lượt 1 trước CP3; gom ≥3 lỗi thành nhóm có tên; sửa đúng nhóm lỗi đau nhất (thường là Grader chấm "hiểu" sai); lượt 2 trên **cùng** 28 câu; `eval/README.md` một trang.

### R6 · Chi phí (12)
- **Mạnh:** 3 persona, 3 kịch bản, ≥2 mức model, giá có link + ngày xem từ `model-prices.csv`.
- **Yếu:** số task / tháng của persona là *(tự ước tính)*; `simulate` phải chạy **thật qua bản chạy thử** ≥50 phiên với seed cố định, token đọc từ log; chi phí / task thành công phải dùng tỉ lệ đạt lượt 2.
- **Để tối đa:** thêm câu "tuần qua bạn làm bao nhiêu task có dùng AI?" vào khảo sát để persona có nguồn; một dòng so chi phí / người với impact / người.

### R7 · Slide & demo (10)
- **Mạnh:** demo 2 phút có kịch tính (trả lời sai → bị chỉ ra khái niệm hổng; comment chèn lệnh không lừa được Grader).
- **Yếu:** giám khảo sẽ đưa câu thử lạ tại chỗ; ai trong nhóm cũng phải giải thích được DI, vì sao chọn workflow, chi phí / task.
- **Để tối đa:** slide 8 trang theo guide 5.1, mỗi trang ≥1 số có nguồn; video dự phòng; tập trả lời 4 câu hỏi vặn.

### Bonus (+5)
- 2–3 junior ngoài nhóm dùng thử Check sáng mai, ghi `validation/log.md` đủ cột, rút ra ≥1 thay đổi. Dùng luôn để đo chỉ số học (bài biến thể không AI).

### Trừ điểm cần tránh
- **API key:** project P-140 trên máy bạn có `.env` chứa key. Không chép file đó sang repo này. Kiểm `.gitignore` có `.env`.
- **Log thật của người dùng thử** không commit vào repo công khai.
- Không sửa chuẩn "đạt", câu thử, kết quả lượt đã chạy sau khi chốt.

## 5 việc ưu tiên (giờ Việt Nam)
1. **Trước 17:00 hôm nay:** push repo (cấp quyền GitHub hoặc tự push), điền đủ `TEAMS.md`, `canvas.md` + thẻ đề F, đưa lab coach xem thẻ đề, nộp CP1.
2. **Ngay sau CP1:** phát khảo sát cho junior / sinh viên IT ngoài nhóm, hẹn 3 phỏng vấn + 1 senior.
3. **Trước 19:30:** chốt `metric_spec.yaml` + chuẩn "đạt" trong `spec.md` §7, benchmark ≥10 câu, `run.py` chạy với AI giả, nộp CP2.
4. **Trước khi ngủ:** Check (Examiner + Grader) gọi model thật qua `run.py`; đủ 28 câu; thử nghiệm "giải thích lại" để có câu nguồn thật.
5. **Trước CP3 10:00 → CP4 14:30:** lượt 1 + video 30 giây, `evidence/summary.md` ≥5 trích dẫn; lượt 2, `simulate` 50 phiên, `demo-slides.pdf`. Extension chỉ làm khi những việc này đã xong.
