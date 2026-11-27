# Chi phí khi dùng thật

> Nhóm Ricin · CodeOwn · phần C (Lê Thành Nguyên). Nộp CP4 14:30 Thứ Bảy 28/11.
> Số ở mục 2 **không điền tay**: `cost/personas.yaml` → `python run.py simulate --rate-from eval/run-2.csv` → chép bảng trong `cost/simulate-N-summary.md`.
> Lúc build dùng gói miễn phí vẫn tính theo **giá gói trả phí**.

## 1. Đầu vào

- **Persona** (`cost/personas.yaml`): `sinh_vien_do_an` 0,4 × 15 task / tháng · `junior_di_lam` 0,4 × 40 · `tu_hoc_chuyen_nganh` 0,2 × 20; mỗi phiên = 1 task trọn vẹn (`agent.py` mode `task`: monitor → examine → grade từng câu, có hỏi tiếp → reflect). Nguồn: `docs/design.md` §9.3 *(tự ước tính — thay bằng câu "tuần qua bạn làm bao nhiêu task có dùng AI?" của khảo sát D trước CP4)*
- **Số người dùng thật** 3 kịch bản: thấp 1.000 · cơ sở 10.000 · cao 50.000 *(tự ước tính, `docs/design.md` §9.3)*
- **Giá** (USD / 1M token, https://console.groq.com/docs/models, xem 27/11/2026; nhóm đổi từ Claude sang Groq): `openai/gpt-oss-20b` vào 0,075 / ra 0,30 · `openai/gpt-oss-120b` vào 0,15 / ra 0,60
- **Tỉ lệ đạt** dùng để tính: __/28 (__%) — lượt `run-2` *(chưa chạy)*
- Đo token trên cấu hình __, tính giá gpt-oss-20b và gpt-oss-120b

## 2. Kết quả mô phỏng

Lượt mô phỏng: `cost/simulate-__.csv` · run ID __ · __ phiên · seed 42 — **chưa có**: simulate chỉ được tính khi bản chạy thử gọi model thật (lượt 27/11 chạy bằng nhánh giả → khung ghi `simulate-mock.csv`, không đánh số).

*(dán bảng từ `cost/simulate-N-summary.md`)*

| Model | Chi phí / phiên | Chi phí / task thành công | / tháng — thấp | / tháng — cơ sở | / tháng — cao | / người / tháng (cơ sở) |
|---|---|---|---|---|---|---|
| | | | | | | |
| | | | | | | |

Chi phí / task thành công = chi phí trung bình mỗi phiên ÷ tỉ lệ đạt — **không coi như đạt 100%**.

**Ước tính trước khi đo** *(tự ước tính, `docs/design.md` §9.1–9.2 — chỉ để so khi có số đo, không dùng thay số simulate)*: ~37.500 token vào + 5.000 ra / task → trộn gpt-oss-120b (Examiner, Reflector) + gpt-oss-20b (Classifier, Grader) ≈ 0,0067 USD / task · toàn 20b ≈ 0,0043 · toàn 120b ≈ 0,0086.

## 3. So với impact

- Impact / người / tháng (`spec.md` §2): ~6 giờ / người bị ảnh hưởng *(tự ước tính)*
- Chi phí / người / tháng (cơ sở, cấu hình trộn): __ *(ước tính trước khi đo: ~1,9 USD)*
- **Kết luận một dòng — đáng làm không:** __ *(điền sau simulate)*

## 4. *(Muốn sâu hơn, không bắt buộc)*

- Cần gạt đã thiết kế sẵn để thử ở lượt 2: toàn gpt-oss-20b thay vì trộn (giữ được `bo_sot_chua_hieu` ≤10% thì rẻ ~1,6 lần) · Classifier chạy chế độ chỉ luật (bớt ~15 lần gọi / task) · giám khảo thứ hai chỉ bật khi `hieu` + tự tin thấp.
- Chi phí ngoài model: gần 0 — lõi chạy trên máy người dùng, không có server; người dùng tự trả API key.
