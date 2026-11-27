# Python decimal — tính tiền không sai số
link: https://docs.python.org/3/library/decimal.html
nguon: tóm tắt do nhóm tự viết lại, chưa đối chiếu từng câu với trang gốc

float lưu số theo hệ nhị phân nên 0.1 + 0.2 không đúng bằng 0.3. Decimal lưu số thập phân chính xác, hợp với tiền.

Tạo Decimal từ chuỗi (Decimal("1.1") hoặc Decimal(str(x))), không từ float. quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) làm tròn 2 chữ số theo kiểu nửa lên. Chuỗi không phải số làm Decimal ném InvalidOperation.
