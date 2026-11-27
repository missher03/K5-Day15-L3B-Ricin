# MDN AbortController và fetch — timeout, retry
link: https://developer.mozilla.org/en-US/docs/Web/API/AbortController
nguon: tóm tắt do nhóm tự viết lại, chưa đối chiếu từng câu với trang gốc

AbortController cho phép huỷ một fetch: truyền controller.signal vào fetch, gọi controller.abort() thì promise của fetch bị từ chối với lỗi tên AbortError. Kết hợp setTimeout để làm timeout, và clearTimeout trong finally để dọn hẹn giờ.

fetch chỉ từ chối khi lỗi mạng hoặc bị huỷ; HTTP 4xx / 5xx vẫn trả về bình thường, cần kiểm res.ok hoặc res.status. Lỗi 5xx và lỗi mạng thường đáng thử lại; 4xx là lỗi phía client, thử lại vô ích. Chờ tăng dần (exponential backoff) giữa các lần thử để không dồn tải lên server.
