# Python threading.Lock và time.monotonic — cache có hạn dùng
link: https://docs.python.org/3/library/time.html#time.monotonic
nguon: tóm tắt do nhóm tự viết lại, chưa đối chiếu từng câu với trang gốc

time.monotonic() là đồng hồ chỉ tăng, không nhảy khi đổi giờ hệ thống, hợp để đo khoảng thời gian như hạn TTL. time.time() có thể lùi hoặc nhảy.

threading.Lock dùng với "with lock:" để chỉ một luồng sửa dict chung tại một thời điểm, tránh hai luồng cùng đọc - sửa - ghi làm hỏng dữ liệu (https://docs.python.org/3/library/threading.html#lock-objects).
