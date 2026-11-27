# Python hmac.compare_digest — so sánh thời gian hằng
link: https://docs.python.org/3/library/hmac.html#hmac.compare_digest
nguon: tóm tắt do nhóm tự viết lại, chưa đối chiếu từng câu với trang gốc

hmac.compare_digest(a, b) so sánh hai chuỗi hoặc bytes và trả True / False. Thời gian chạy không phụ thuộc vị trí ký tự sai đầu tiên, nên kẻ tấn công không đo thời gian phản hồi để đoán dần từng ký tự (timing attack).

Phép so sánh == thông thường có thể dừng ngay ở ký tự khác đầu tiên. Khi so sánh hash mật khẩu, token, chữ ký, nên dùng compare_digest thay cho ==.
