# Chi phí khi dùng thật

> Nhóm Ricin · CodeOwn · phần C (Lê Thành Nguyên). Nộp CP4 14:30 Thứ Bảy 28/11.
> Số ở mục 2 **không điền tay**: `cost/personas.yaml` → `python run.py simulate` (tự lấy tỉ lệ đạt lượt mới nhất, `run-5`) → chép bảng trong `cost/simulate-1-summary.md`.
> Lúc build dùng gói miễn phí vẫn tính theo **giá gói trả phí**.

## 1. Đầu vào

- **Persona** (`cost/personas.yaml`): `sinh_vien_do_an` 0,412 × 15 task / tháng · `junior_di_lam` 0,294 × 40 · `tu_hoc_chuyen_nganh` 0,294 × 20 (≈23,8 task / người / tháng); mỗi phiên = 1 task trọn vẹn (`agent.py` mode `task`: monitor → examine → grade từng câu, có hỏi tiếp → reflect). Tỉ lệ persona: khảo sát 27/11 (7/17, 5/17, 5/17 người dùng đích; simulate-1 chạy với tỉ lệ này). Sau 3 phiếu thêm 28/11 tỉ lệ thành 7/20, 8/20, 5/20 — chưa chạy lại simulate, ước tính tay ~26 task / người / tháng, chi phí / người / tháng cao hơn ~10%. Số task / tháng: *(tự ước tính, `docs/design.md` §9.3 — form khảo sát không hỏi số task)*
- **Số người dùng thật** 3 kịch bản: thấp 1.000 · cơ sở 10.000 · cao 50.000 *(tự ước tính, `docs/design.md` §9.3)*
- **Giá** (USD / 1M token, bảng giá BTC `model-prices.md` 25/11/2026, khớp https://platform.claude.com/docs/en/about-claude/pricing xem 27/11/2026): Claude Haiku 5.5 vào 0,10 / ra 0,50 · Claude Sonnet 5.5 vào 2,00 / ra 10,00
- **Tỉ lệ đạt** dùng để tính: 27/28 (96%) — lượt 2 `run-5@20261128-103708`
- Đo token trên cấu hình lượt 1/2 (Haiku 5.5 cho Classifier + Grader, Sonnet 5.5 cho Examiner + Reflector + giám khảo thứ hai), tính giá Haiku 5.5 và Sonnet 5.5 theo đúng model từng lần gọi

## 2. Kết quả mô phỏng

Lượt mô phỏng: `cost/simulate-1.csv` · run ID `simulate-1@20261128-104057` · 50 phiên · seed 42 · 0/50 phiên lỗi · trace `traces/simulate-1.jsonl` · bảng gốc `cost/simulate-1-summary.md`.

| Persona | Số phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|
| sinh_vien_do_an | 22 | 17.625 | 2.752 | 8,1 | 7,3 |
| junior_di_lam | 10 | 15.301 | 2.633 | 6,9 | 6,9 |
| tu_hoc_chuyen_nganh | 18 | 19.053 | 3.040 | 8,8 | 7,8 |

| Model | Chi phí / phiên | Chi phí / task thành công | / tháng — thấp (1.000) | / tháng — cơ sở (10.000) | / tháng — cao (50.000) | / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|
| **Thực đo** (Haiku 5.5 + Sonnet 5.5, giá riêng từng model) | $0,0312 | $0,0324 | $737 | $7.368 | $36.841 | $0,74 |
| Nếu mọi token tính giá Haiku 5.5 | $0,0032 | $0,0033 | $73 | $729 | $3.646 | $0,07 |
| Nếu mọi token tính giá Sonnet 5.5 | $0,0637 | $0,0660 | $1.458 | $14.583 | $72.915 | $1,46 |

**Đọc số này thế nào:**
- **3/50 phiên token = 0** (S008 `repo07_c1` diff chỉ đổi định dạng / tên; S019, S042 `repo12_c1` diff chỉ docs): Check bỏ qua đúng thiết kế nên không gọi model. Ba phiên này vẫn tính vào trung bình vì người dùng thật cũng có commit kiểu này. Nếu bỏ ra, trung bình 47 phiên còn lại là ~$0,0332 / phiên, ~$0,0344 / task thành công.
- **Chi phí / tháng là ngoại suy**, không phải số đo: nhân chi phí / phiên đo thật với số người dùng (1.000 / 10.000 / 50.000) và số task / người / tháng (~23,8), cả hai đều *tự ước tính, chưa đo*. Chỉ chi phí / phiên và tỉ lệ đạt là số đo.
- Câu trả lời trong mô phỏng lấy từ `sim_answers.json` (giả lập), nên số vòng hỏi lại của người thật có thể khác → token / phiên có thể lệch.

Chi phí / task thành công = chi phí trung bình mỗi phiên ÷ tỉ lệ đạt — **không coi như đạt 100%**.

**Ước tính trước khi đo** *(tự ước tính, `docs/design.md` §9.1–9.2 — chỉ để so khi có số đo, không dùng thay số simulate)*: ~37.500 token vào + 5.000 ra / task → trộn Sonnet (Examiner, Reflector) + Haiku (Classifier, Grader) ≈ 0,074 USD / task · toàn Haiku ≈ 0,006 · toàn Sonnet ≈ 0,13.

## 3. So với impact

- Impact / người / tháng (`spec.md` §2): ~6 giờ / người bị ảnh hưởng *(tự ước tính)*
- Chi phí / người / tháng (cơ sở, cấu hình trộn): **~0,74 USD** (đo chi phí / phiên, số task / tháng tự ước tính) — thấp hơn ước tính trước khi đo (~1,9 USD) vì token thật / task ~17.600 vào + 2.800 ra, chỉ khoảng một nửa ước tính 37.500 + 5.000.
- **Kết luận một dòng — đáng làm không:** đáng làm: ~0,74 USD / người / tháng (người dùng tự trả bằng API key) so với 1–3 giờ mỗi lần bị kẹt vì code AI không hiểu (phỏng vấn 27/11); cần đo số task / tháng thật trước khi tin con số tháng.

## 4. *(Muốn sâu hơn, không bắt buộc)*

- Cần gạt đã thiết kế sẵn để thử ở lượt 2: toàn Haiku thay vì trộn (giữ được `bo_sot_chua_hieu` ≤10% thì rẻ ~12 lần) · Classifier chạy chế độ chỉ luật (bớt ~15 lần gọi / task) · giám khảo thứ hai chỉ bật khi `hieu` + tự tin thấp.
- Chi phí ngoài model: gần 0 — lõi chạy trên máy người dùng, không có server; người dùng tự trả API key.
