# Python sqlite3 — tham số hoá truy vấn bằng dấu ?
link: https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders
nguon: tóm tắt do nhóm tự viết lại, chưa đối chiếu từng câu với trang gốc

Truyền giá trị bằng dấu ? và một tuple riêng: conn.execute("SELECT * FROM t WHERE id = ?", (x,)). Thư viện gửi giá trị tách khỏi câu lệnh, nên chuỗi người dùng nhập không bao giờ thành một phần câu lệnh SQL. Đây là cách chặn SQL injection, không phải "escape chuỗi" bằng tay.

Không ghép giá trị vào câu SQL bằng f-string hay dấu +. cursor.rowcount cho biết số dòng câu UPDATE / DELETE vừa đụng tới; bằng 0 nghĩa là không có dòng nào khớp.

LIKE ... ESCAPE '\' cho phép coi % và _ do người dùng gõ là ký tự thường thay vì ký tự đại diện.
