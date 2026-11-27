# Tóm tắt mô phỏng simulate-1@20261127-193252

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| sinh_vien_do_an | 22 | 1 | 16204 | 2858 | 8.0 | 7.2 |
| junior_di_lam | 14 | 1 | 13289 | 2327 | 6.2 | 6.9 |
| tu_hoc_chuyen_nganh | 14 | 1 | 19859 | 3422 | 10.1 | 8.0 |

Tỉ lệ đạt dùng để tính: 25/28 (89%) — lượt run-3@20261127-181857

- Tỉ lệ đạt lấy từ lượt nhóm chọn: eval/run-3.csv (--rate-from).

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (1.000 người) | Chi phí / tháng — cơ sở (10.000 người) | Chi phí / tháng — cao (50.000 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Thực đo — mỗi model giá riêng** (claude-haiku-5-5 + claude-sonnet-5-5) | $0.0314 | $0.0352 | $0.0352 | $793.73 | $7,937.35 | $39,686.74 | $0.7937 |
| claude-haiku-5-5 (vào 0.1 · ra 0.5 $/1M) — nếu MỌI token tính giá model này | $0.0031 | $0.0034 | $0.0034 | $72.96 | $729.65 | $3,648.24 | $0.0730 |
| claude-sonnet-5-5 (vào 2.0 · ra 10.0 $/1M) — nếu MỌI token tính giá model này | $0.0615 | $0.0689 | $0.0689 | $1,459.30 | $14,592.97 | $72,964.84 | $1.46 |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (1.0) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: claude-haiku-5-5, claude-sonnet-5-5. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 0/50.
