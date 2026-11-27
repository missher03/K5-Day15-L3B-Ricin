# Python hashlib.pbkdf2_hmac — băm mật khẩu có salt
link: https://docs.python.org/3/library/hashlib.html#hashlib.pbkdf2_hmac
nguon: tóm tắt do nhóm tự viết lại, chưa đối chiếu từng câu với trang gốc

pbkdf2_hmac(hash_name, password, salt, iterations) băm mật khẩu lặp nhiều vòng để mỗi lần đoán thử tốn thời gian. Số vòng lặp càng lớn thì dò mật khẩu càng chậm.

Salt là chuỗi ngẫu nhiên riêng cho mỗi mật khẩu (vd os.urandom(16)), lưu cùng hash. Nhờ salt, hai người cùng mật khẩu có hash khác nhau và bảng tra hash dựng sẵn (rainbow table) không dùng được.
