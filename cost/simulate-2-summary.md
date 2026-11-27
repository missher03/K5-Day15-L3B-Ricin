# Tóm tắt mô phỏng simulate-2@20261127-195553

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| sinh_vien_do_an | 22 | 1 | 15442 | 4756 | 7.6 | 7.4 |
| junior_di_lam | 14 | 1 | 14068 | 4271 | 6.7 | 6.9 |
| tu_hoc_chuyen_nganh | 13 | 1 | 18751 | 5442 | 9.5 | 8.1 |

Tỉ lệ đạt dùng để tính: 24/28 (86%) — lượt run-4@20261127-193252

- Tỉ lệ đạt lấy từ lượt nhóm chọn: eval/run-4.csv (--rate-from).

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (1.000 người) | Chi phí / tháng — cơ sở (10.000 người) | Chi phí / tháng — cao (50.000 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| claude-haiku-5-5 (vào 0.1 · ra 0.5 $/1M) | $0.0040 | $0.0047 | $0.0047 | $98.59 | $985.91 | $4,929.55 | $0.0986 |
| claude-sonnet-5-5 (vào 2.0 · ra 10.0 $/1M) | $0.0798 | $0.0932 | $0.0932 | $1,971.82 | $19,718.22 | $98,591.10 | $1.97 |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (1.0) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: claude-haiku-5-5. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 1/50.
