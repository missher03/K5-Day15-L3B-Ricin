# Tóm tắt mô phỏng simulate-1@20261128-104057

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| sinh_vien_do_an | 22 | 1 | 17625 | 2752 | 8.1 | 7.3 |
| junior_di_lam | 10 | 1 | 15301 | 2633 | 6.9 | 6.9 |
| tu_hoc_chuyen_nganh | 18 | 1 | 19053 | 3040 | 8.8 | 7.8 |

Tỉ lệ đạt dùng để tính: 27/28 (96%) — lượt run-5@20261128-103708

- Tự chọn: lượt run-N mới nhất đã chấm xong, chạy bằng đúng model đang đo (run-5.csv). Muốn dùng lượt khác (vd lượt 2): thêm `--rate-from eval/run-2.csv`.

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (1.000 người) | Chi phí / tháng — cơ sở (10.000 người) | Chi phí / tháng — cao (50.000 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Thực đo — mỗi model giá riêng** (claude-haiku-5-5 + claude-sonnet-5-5) | $0.0312 | $0.0324 | $0.0324 | $736.83 | $7,368.28 | $36,841.42 | $0.7368 |
| claude-haiku-5-5 (vào 0.1 · ra 0.5 $/1M) — nếu MỌI token tính giá model này | $0.0032 | $0.0033 | $0.0033 | $72.92 | $729.15 | $3,645.76 | $0.0729 |
| claude-sonnet-5-5 (vào 2.0 · ra 10.0 $/1M) — nếu MỌI token tính giá model này | $0.0637 | $0.0660 | $0.0660 | $1,458.31 | $14,583.06 | $72,915.29 | $1.46 |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (1.0) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: claude-haiku-5-5, claude-sonnet-5-5. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 0/50.
