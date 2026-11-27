# Kịch bản phỏng vấn — 3 Junior + 1 Senior (15 phút / người)

> Theo `docs/design.md` §2.3 và `evidence/interviews/TEMPLATE.md`.
> **Nguyên tắc:** chỉ hỏi **chuyện thật đã xảy ra**, không giới thiệu sản phẩm. Không ghi tên thật, SĐT, email, tên công ty — chỉ ghi `P1`, `P2`, `P3` (junior) và `P4` (senior). Khi tổng hợp với nhóm nhỏ (3 người), **chỉ ghi `x/3 người`, không ghi %**.

---

## 0. Tin nhắn hẹn (15 phút)

- **Gửi junior:** *"Chào bạn, nhóm mình đang tìm hiểu cách lập trình viên mới làm việc với code do AI viết. Cho mình hỏi 15 phút qua call về task gần nhất bạn dùng AI được không? Không giới thiệu sản phẩm, không ghi tên hay công ty."*
- **Gửi senior / tech lead:** *"Chào anh/chị, nhóm em đang tìm hiểu tình hình review PR có dùng AI của các bạn junior. Anh/chị cho em xin 15 phút hỏi về các PR gần đây anh/chị review được không ạ? Ẩn danh hoàn toàn, không quảng cáo gì ạ."*

---

## 1. Câu hỏi cho 3 Junior (`P1.md`, `P2.md`, `P3.md` — ≤2 năm KN)

1. Bạn đang làm vai trò gì (sinh viên năm mấy / fresher / junior mấy tháng) và tuần vừa rồi bạn làm khoảng bao nhiêu task có dùng AI?
2. **Task gần nhất bạn dùng AI viết code là gì?** Bạn làm từng bước ra sao từ lúc mở AI đến lúc commit / nộp?
3. **Trong task đó (hoặc 1 tháng qua), có đoạn nào bạn nộp mà không hiểu rõ nó chạy thế nào không?** Đoạn đó làm chức năng gì?
4. **Chuyện gì xảy ra sau đó?** (Có bị reviewer / giảng viên hỏi lại, PR bị trả lại, hay gặp lỗi mà tự sửa không được không?)
5. Lần kẹt gần nhất đó bạn mất khoảng **bao nhiêu phút / giờ** để gỡ, và bạn xoay xở bằng cách nào?
6. Trong **1 tháng qua**, chuyện như vậy xảy ra khoảng **mấy lần**? Hiện bạn có cách nào để tự kiểm tra mình đã hiểu code AI viết chưa — và vì sao hay bỏ qua?

---

## 2. Câu hỏi cho 1 Senior / Tech Lead (`P4.md` — >2 năm KN, có review PR junior)

1. Anh/chị thường review code cho khoảng bao nhiêu bạn junior/fresher, mỗi tuần khoảng bao nhiêu PR?
2. Trong **1 tháng qua**, có khoảng **bao nhiêu PR của junior bị trả lại (hoặc phải hỏi lại)** vì bạn ấy không giải thích được đoạn code mình nộp (nghi do AI viết)?
3. **Mỗi tuần** anh/chị mất tổng cộng khoảng **bao nhiêu giờ** cho việc hỏi lại, giải thích và review lại những PR kiểu này? (Và trung bình **mỗi lần** mất khoảng bao nhiêu phút?)
4. Kể giúp em **trường hợp gần nhất**: đoạn code sai hoặc khó hiểu ở đâu, lúc anh/chị hỏi thì bạn junior trả lời thế nào?
5. Team anh/chị hiện xử lý việc này bằng cách nào, và cách đó còn vướng ở đâu?

---

## 3. Cần lưu lại những gì?

Chép `evidence/interviews/TEMPLATE.md` thành **`P1.md`**, **`P2.md`**, **`P3.md`**, **`P4.md`** trong `evidence/interviews/`, mỗi file bắt buộc có:
- **Tiêu đề ẩn danh:** `P1 · junior backend 1 năm · call · 27/11 20:00 · hỏi: TV4 · ghi: TV4`
- **Nguyên danh sách câu đã hỏi** + ghi chép ngắn theo thứ tự kể
- **Các con số nghe được** (không nhớ thì ghi *"không nhớ"*, không tự đoán):
  - Junior (`P1`–`P3`): lần gần nhất · số lần/tháng · số phút mất lần đó · cách xoay xở
  - Senior (`P4`): số PR bị trả lại/tháng · **số giờ mất mỗi tuần** · số phút mất mỗi lần *(dùng trực tiếp cho Impact)*
- **1–2 câu trích nguyên văn** (đã xoá tên công ty/người) để đưa sang `evidence/summary.md`
- **Kết luận 1 dòng:** Có / Không / Một phần gặp pain, và điểm nào **ngược** với giả thuyết nhóm.
