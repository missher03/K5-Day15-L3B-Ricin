# Chi phí khi dùng thật

> Nhóm Ricin · CodeOwn · phần C (Lê Thành Nguyên). Nộp CP4 14:30 Thứ Bảy 28/11.
> Số ở mục 2 **không điền tay**: chép từ `cost/simulate-1-summary.md` và `cost/simulate-2-summary.md` do `python run.py simulate` sinh.
> Lúc build dùng gói miễn phí vẫn tính theo **giá gói trả phí**.

## 1. Đầu vào

- **Persona** (`cost/personas.yaml`): `sinh_vien_do_an` 0,4 × 15 task / tháng · `junior_di_lam` 0,4 × 40 · `tu_hoc_chuyen_nganh` 0,2 × 20 → trung bình 26 task / người / tháng. Mỗi phiên = **1 task trọn vẹn** (`agent.py` mode `task`: Monitor → Examiner → Grader từng câu, có hỏi tiếp và bỏ phiếu → Reflector), chạy thật qua lõi A + B. Nguồn: `docs/design.md` §9.3 *(tự ước tính — `evidence/summary.md` chưa có số khảo sát; thay bằng câu "tuần qua bạn làm bao nhiêu task có dùng AI?" khi D có)*
- **Số người dùng thật** 3 kịch bản: thấp 1.000 · cơ sở 10.000 · cao 50.000 *(tự ước tính, `docs/design.md` §9.3)*
- **Giá** (USD / 1M token, https://platform.claude.com/docs/en/about-claude/pricing, xem 27/11/2026): Claude Haiku 5.5 vào 0,10 / ra 0,50 · Claude Sonnet 5.5 vào 2,00 / ra 10,00
- **Tỉ lệ đạt** dùng để tính — mỗi cấu hình lấy đúng lượt eval chạy bằng chính cấu hình đó:
  - trộn Haiku + Sonnet: **25/28 (89%)** — `run-3` (lượt 2)
  - toàn Haiku: **24/28 (86%)** — `run-4` (cùng code lượt 2, `eval/report.md` mục 5)
- Đo token trên chính cấu hình đó; dòng "nếu MỌI token tính giá model X" chỉ là quy đổi giá trên cùng số token, không phải lượt đo.

## 2. Kết quả mô phỏng

### Cấu hình trộn (cơ sở thiết kế): Haiku 5.5 cho Grader + Classifier, Sonnet 5.5 cho Examiner + Reflector + giám khảo thứ hai

Lượt mô phỏng: `cost/simulate-1.csv` · run ID simulate-1@20261127-193252 · 50 phiên (0 lỗi) · seed 42 · trung bình 8,1 lần gọi model, 16.411 token vào, 2.867 ra / task

| Model | Chi phí / phiên (= / task) | Chi phí / task thành công | / tháng — thấp | / tháng — cơ sở | / tháng — cao | / người / tháng (cơ sở) |
|---|---|---|---|---|---|---|
| **Thực đo — mỗi model giá riêng** (Haiku 5.5 + Sonnet 5.5) | $0.0314 | $0.0352 | $793.73 | $7,937.35 | $39,686.74 | $0.79 |
| *(quy đổi)* mọi token giá Haiku 5.5 | $0.0031 | $0.0034 | $72.96 | $729.65 | $3,648.24 | $0.07 |
| *(quy đổi)* mọi token giá Sonnet 5.5 | $0.0615 | $0.0689 | $1,459.30 | $14,592.97 | $72,964.84 | $1.46 |

### Cấu hình rẻ: toàn Haiku 5.5

Lượt mô phỏng: `cost/simulate-2.csv` · run ID simulate-2@20261127-195553 · 50 phiên (**1 lỗi**: S023 `repo06_c1` — Haiku chạm `max_tokens`, output bị cắt, không tính vào trung bình) · seed 42 · trung bình 7,9 lần gọi model, 15.913 token vào, 4.759 ra / task

| Model | Chi phí / phiên (= / task) | Chi phí / task thành công | / tháng — thấp | / tháng — cơ sở | / tháng — cao | / người / tháng (cơ sở) |
|---|---|---|---|---|---|---|
| **Thực đo** claude-haiku-5-5 | $0.0040 | $0.0047 | $98.59 | $985.91 | $4,929.55 | $0.10 |
| *(quy đổi)* mọi token giá Sonnet 5.5 | $0.0798 | $0.0932 | $1,971.82 | $19,718.22 | $98,591.10 | $1.97 |

Chi phí / task thành công = chi phí trung bình mỗi phiên ÷ tỉ lệ đạt — **không coi như đạt 100%**.

**So với ước tính trước khi đo** (`docs/design.md` §9.1–9.2, *tự ước tính*): đã đoán ~37.500 token vào + 5.000 ra / task → trộn ≈ 0,074 USD / task. Đo được ~16.400 vào + 2.900 ra → **0,031 USD**, thấp hơn ~2,4 lần. Một phần vì Monitor không gọi model (xem dưới, ước tính cũ tính 15 lần gọi Classifier); phần còn lại chưa phân tích theo từng bước.

**Chưa tính trong số đo:**
- **Classifier gọi model**: trong eval / simulate, Monitor phân loại prompt **bằng luật** (`tools.monitor_offline` của lõi A), không gọi model. Nếu bật Classifier dùng Haiku cho ~15 prompt / task: thêm khoảng 7.500 token vào + 300 ra ≈ **0,0009 USD / task** *(tự ước tính, `docs/design.md` §9.1)* — không đổi kết luận.
- Câu trả lời của người dùng là câu giả lập (`data/samples/*/sim_answers.json`), 3 mức cố định; người thật trả lời dài / ngắn khác thì token Grader khác.

## 3. So với impact

- Impact / người / tháng (`spec.md` §2): ~6 giờ / người bị ảnh hưởng *(tự ước tính — chờ số khảo sát / phỏng vấn senior)*
- Chi phí / người / tháng (cơ sở, 26 task): **0,79 USD** cấu hình trộn · **0,10 USD** toàn Haiku. Tính theo task thành công: 0,035 và 0,0047 USD / task.
- **Kết luận một dòng — đáng làm không:** đáng — dưới 1 USD / người / tháng (người dùng tự trả qua API key của họ) so với ~6 giờ làm lại / người bị ảnh hưởng / tháng; toàn Haiku rẻ hơn ~8 lần mà vẫn đạt chuẩn (86% so với 89%, cùng `bo_sot_chua_hieu` 0%), nên là cấu hình mặc định hợp lý khi đã sửa lỗi `max_tokens`.

## 4. *(Muốn sâu hơn, không bắt buộc)*

- **Độ nhạy theo cần gạt (đo được):** Sonnet → Haiku cho Examiner + Reflector: 0,0314 → 0,0040 USD / task (÷ ~8), tỉ lệ đạt 89% → 86%, token ra tăng 66% (Haiku viết dài hơn) và 1/50 phiên chạm `max_tokens` → nếu chọn toàn Haiku cần nâng `max_tokens` của tầng mạnh.
- Theo persona (cấu hình trộn, token vào / task · lần gọi model): `tu_hoc_chuyen_nganh` 19.859 · 10,1 · `sinh_vien_do_an` 16.204 · 8,0 · `junior_di_lam` 13.289 · 6,2 — chênh nhau do mỗi persona lấy một nhóm repo mẫu khác nhau (`cost/personas.yaml`), chưa tách nguyên nhân.
- Chi phí ngoài model: gần 0 — lõi chạy trên máy người dùng, không có server, không lưu dữ liệu tập trung; người dùng tự trả API key.
- Giới hạn: 50 phiên × 1 task, câu trả lời giả lập, persona tự ước tính — số / tháng là bậc độ lớn, không phải dự báo.
