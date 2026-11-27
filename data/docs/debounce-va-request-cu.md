# Debounce và bỏ kết quả request cũ
link: https://developer.mozilla.org/en-US/docs/Web/API/setTimeout
nguon: tóm tắt do nhóm tự viết lại, chưa đối chiếu từng câu với trang gốc

Debounce: mỗi lần sự kiện xảy ra thì clearTimeout hẹn giờ cũ và đặt hẹn giờ mới; hàm chỉ chạy khi sự kiện ngừng đủ waitMs. Ô tìm kiếm nhờ vậy không gọi API mỗi lần gõ phím.

Request về không theo thứ tự gửi. Giữ một bộ đếm (requestId) và bỏ kết quả của request không phải mới nhất để màn hình không hiện kết quả cũ.
