# Python csv.DictReader và mã hoá utf-8-sig
link: https://docs.python.org/3/library/csv.html#csv.DictReader
nguon: tóm tắt do nhóm tự viết lại, chưa đối chiếu từng câu với trang gốc

csv.DictReader đọc mỗi dòng thành dict theo dòng tiêu đề. Nên mở file với newline="" như docs khuyên, để ô có xuống dòng được đọc đúng.

File CSV do Excel lưu dạng "CSV UTF-8" có ký tự BOM ở đầu. Mở bằng encoding="utf-8-sig" để bỏ BOM; nếu không, tên cột đầu tiên sẽ dính ký tự lạ (\ufeff) và row.get("cột") trả None.
