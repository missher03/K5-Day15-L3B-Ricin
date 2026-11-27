# OWASP — upload file an toàn, chặn path traversal
link: https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html
nguon: tóm tắt do nhóm tự viết lại, chưa đối chiếu từng câu với trang gốc

Không dùng tên file người dùng gửi để lưu: tên có thể chứa ../ để ghi ra ngoài thư mục upload (path traversal). Đặt tên mới do server sinh (vd uuid) và chỉ giữ phần đuôi đã kiểm.

Giới hạn dung lượng, chỉ cho phép danh sách đuôi file cần thiết, và kiểm đường dẫn cuối cùng (sau abspath) vẫn nằm trong thư mục upload.
