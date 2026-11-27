# Khảo sát — bộ câu hỏi CodeOwn · Nhóm Ricin

> Theo `docs/design.md` §2.3 và `task.md` mục D. Hỏi **hành vi đã xảy ra** (tuần / tháng qua), không hỏi "có thích không", không giới thiệu sản phẩm.
> **Không thu tên, email, mã học viên** (trừ câu E1 nếu người trả lời tự để lại; cột đó phải xoá trước khi commit `results.csv`).
> Tạo Google Form tự động: chạy [`create_form.gs`](create_form.gs) (hướng dẫn ở cuối file này), hoặc chép tay từng câu dưới đây.

## Thông tin phát form (điền khi phát)

| Mục | Giá trị |
|---|---|
| Link form | ____ |
| Giờ mở | ____ (T6 27/11) |
| Giờ chốt | **9:00 T7 28/11** (mục tiêu ≥20 người ≤2 năm kinh nghiệm, ngoài nhóm) |
| Kênh đã gửi | ____ (vd: nhóm lớp L3B · nhóm dev Facebook ___ · bạn đại học · đồng nghiệp thực tập) |
| Ai gửi kênh nào | A: ___ · B: ___ · C: ___ · D: ___ (mỗi người ≥5 người quen ngoài nhóm) |

## Tiêu đề và lời mở đầu form

**Tiêu đề:** Lập trình viên mới dùng công cụ AI viết code: chuyện thực tế tuần qua (4–6 phút)

**Mô tả:**
> Chào bạn, nhóm mình (sinh viên khoá AI20K) đang tìm hiểu cách lập trình viên mới làm việc với code do công cụ AI (Copilot, Cursor, ChatGPT, Claude…) viết. Các câu hỏi chỉ hỏi về **những gì đã xảy ra** trong tuần / tháng vừa qua, không có đúng sai. Form **không thu tên hay email**. Câu trả lời chỉ dùng tổng hợp số liệu cho bài hackathon. Cảm ơn bạn!

---

## Phần A — Câu lọc (bắt buộc)

| # | Câu hỏi | Kiểu trả lời | Rẽ nhánh |
|---|---|---|---|
| A1 | Bạn đã lập trình **có trả lương / thực tập / làm đồ án thật** được bao lâu? | Chọn một: Chưa đi làm, đang là sinh viên · Dưới 6 tháng · 6–12 tháng · 1–2 năm · Trên 2 năm | "Trên 2 năm" → **Phần D** (senior) |
| A2 | Hiện tại bạn là: | Chọn một: Sinh viên IT năm 1–2 · Sinh viên IT năm 3–4 / làm đồ án tốt nghiệp · Fresher / junior đang đi làm · Người tự học / chuyển ngành sang lập trình · Khác | — |
| A3 | **Trong 1 tháng qua**, bạn dùng công cụ AI để viết / sửa code bao thường xuyên? | Chọn một: Hầu như mỗi ngày · Vài lần mỗi tuần · Vài lần trong tháng · Không dùng | "Không dùng" → **Gửi form** (kết thúc) |
| A4 | Bạn đã dùng công cụ nào trong tháng qua? | Chọn nhiều: GitHub Copilot · Cursor · Claude Code · ChatGPT / Claude / Gemini trên web (copy–paste) · Windsurf / Cline / Codex · Khác | — |

## Phần B — Hành vi tuần / tháng qua (bắt buộc, trừ B9)

| # | Câu hỏi | Kiểu trả lời | Dùng cho |
|---|---|---|---|
| B1 | **Tuần vừa qua**, bạn làm bao nhiêu task (bài tập, ticket, tính năng, bug) **có dùng AI để viết code**? | Số (0–100) | Persona chi phí `cost/personas.yaml` (task / tháng ≈ B1 × 4) |
| B2 | Nghĩ về **lần nộp gần nhất** (commit / PR / bài nộp) có code AI viết. Khoảng bao nhiêu phần code trong đó là AI viết và bạn **giữ gần như nguyên**? | Chọn một: Dưới 25% · 25–50% · 50–75% · Trên 75% · Không nhớ | Bối cảnh DI (f1) |
| B3 | Trước khi nộp lần đó, bạn đã đọc phần code AI viết tới mức nào? | Chọn một: Đọc kỹ từng dòng · Đọc lướt phần chính · Chạy thử thấy chạy được là nộp, gần như không đọc · Không nhớ | Luồng hiện tại `spec.md` §0 |
| B4 | **Trong lần nộp gần nhất đó**, có đoạn code quan trọng nào (xử lý lỗi, truy vấn DB, đăng nhập, gọi API…) mà **đến giờ bạn vẫn không giải thích được** nó làm gì hoặc vì sao viết như vậy không? | Chọn một: Có, ít nhất 1 đoạn · Không chắc · Không, giải thích được hết | **Giả thuyết chính** (≥40%) |
| B5 | **Trong 1 tháng qua**, bao nhiêu lần có người (reviewer, giảng viên, người phỏng vấn, đồng đội) hỏi bạn về một đoạn code AI viết mà bạn **không trả lời được**? | Chọn một: 0 · 1 lần · 2–3 lần · 4 lần trở lên · Không nhớ | Impact: số lần / tháng |
| B6 | **Tuần vừa qua**, bao nhiêu lần bạn dán **nguyên thông báo lỗi** vào AI **trước khi tự đọc / đoán** nguyên nhân? | Chọn một: 0 · 1–3 lần · 4–10 lần · Trên 10 lần | Luật nhắc `lap_loi`, f3 |
| B7 | **Trong 1 tháng qua**, bao nhiêu lần bài / PR của bạn **bị trả lại hoặc phải làm lại** vì code AI viết có chỗ sai mà bạn không hiểu? | Chọn một: 0 · 1 lần · 2–3 lần · 4 lần trở lên · Không nhớ | Impact: số lần / tháng |
| B8 | **Lần gần nhất** bạn kẹt vì không hiểu code AI viết, bạn mất bao lâu để gỡ được? | Chọn một: Chưa gặp trong tháng qua · Dưới 15 phút · 15–30 phút · 30–60 phút · 1–2 giờ · Trên 2 giờ / bỏ luôn | Impact: giờ mất mỗi lần |
| B9 | Lần đó bạn đã xoay xở thế nào? | Chọn nhiều: Hỏi lại / dán lỗi lại cho AI · Hỏi senior / bạn bè · Tự đọc docs / Stack Overflow · Tự debug từng dòng · Xoá đi, nhờ AI viết lại từ đầu · Bỏ qua, chưa giải quyết · Chưa gặp · Khác | `spec.md` §1 "hôm nay giải bằng gì" |
| B10 | *(Tuỳ chọn)* Kể ngắn lần gần nhất đó: bạn đang làm gì, kẹt ở đâu, ai phát hiện, hậu quả ra sao? | Đoạn văn | Trích dẫn `evidence/summary.md` §3 |

## Phần C — *(Tuỳ chọn, ~3 phút)* Thử giải thích 2 đoạn code ngắn

> Lời dẫn trên form: *"Phần này không bắt buộc và không phải bài kiểm tra. Bạn cứ trả lời theo cách hiểu của mình, viết bằng lời, **không cần tra Google / hỏi AI**. Không biết thì ghi 'không biết', vậy cũng rất có ích cho nhóm."*

**Đoạn 1 (Python):**
```python
def verify_password(password: str, stored: str) -> bool:
    salt_hex, digest_hex = stored.split("$", 1)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 200_000)
    return hmac.compare_digest(digest.hex(), digest_hex)
```

| # | Câu hỏi | Kiểu | Khớp câu thử |
|---|---|---|---|
| C1 | Dòng cuối so sánh hash bằng `hmac.compare_digest`. Vì sao không dùng `==`? | Đoạn văn | G01 / G09 |
| C2 | Mật khẩu được lưu kèm `salt` (sinh ngẫu nhiên lúc tạo tài khoản). Bỏ salt đi thì sao? | Đoạn văn | G05 |

**Đoạn 2 (JavaScript):**
```js
const res = await fetch(url, { signal: controller.signal });
if (res.status >= 500) throw new Error(`server ${res.status}`);   // nhảy xuống catch để thử lại
if (!res.ok) return { error: `HTTP ${res.status}` };              // 4xx: trả luôn
// ... trong catch:
await new Promise((r) => setTimeout(r, 500 * 2 ** attempt));
```

| # | Câu hỏi | Kiểu | Khớp câu thử |
|---|---|---|---|
| C3 | Vì sao chỉ thử lại khi status ≥ 500, còn lỗi 4xx thì trả về luôn? | Đoạn văn | G03 |
| C4 | Vì sao thời gian chờ trước lần thử tiếp lại tăng dần (500 ms, 1 s, 2 s…)? | Đoạn văn | G08 |

> **Lưu ý trung thực khi dùng Phần C:** đây là câu trả lời thật của người dùng thật, nhưng trên **đoạn code mẫu của nhóm**, không phải code họ tự nộp. Khi đưa vào `eval/real_cases.csv` thì ghi `nguon` = mã phiếu dạng `E101`, `E102`… (khác dải `E1…E8` của thử nghiệm "giải thích lại"), hai người chấm nhãn độc lập rồi thống nhất (`nguoi_cham` = vd `A,C`), và ghi rõ cách lấy trong `data/DATA_CARD.md`. Không sửa câu trả lời cho "đẹp", giữ nguyên chỗ sai.

## Phần D — Dành cho người >2 năm kinh nghiệm (senior / reviewer)

| # | Câu hỏi | Kiểu trả lời | Dùng cho |
|---|---|---|---|
| D1 | Bạn có review code của lập trình viên ≤2 năm kinh nghiệm không? | Chọn một: Có, thường xuyên · Thỉnh thoảng · Không | Lọc |
| D2 | **Trong 1 tháng qua**, bao nhiêu PR / bài của junior mà bạn phải hỏi lại vì họ không giải thích được code (nghi do AI viết)? | Số (0–200) | Impact (phía senior) |
| D3 | Mỗi lần như vậy bạn mất thêm khoảng bao lâu (hỏi, giải thích, review lại)? | Chọn một: Dưới 15 phút · 15–30 phút · 30–60 phút · Trên 1 giờ | Impact: 0,5 giờ senior *(đang tự ước tính)* |
| D4 | *(Tuỳ chọn)* Kể ngắn trường hợp gần nhất. | Đoạn văn | Trích dẫn |
| D5 | *(Tuỳ chọn)* Bạn có sẵn lòng cho nhóm hỏi thêm 15 phút qua call không? Nếu có, để lại cách liên hệ. | Trả lời ngắn | Phỏng vấn senior |

## Phần E — Kết thúc (junior)

| # | Câu hỏi | Kiểu trả lời |
|---|---|---|
| E1 | *(Tuỳ chọn)* Bạn có sẵn lòng cho nhóm hỏi thêm 10–15 phút, hoặc dùng thử một công cụ nhỏ trên VS Code vào sáng 28/11 không? Nếu có, để lại cách liên hệ (Zalo / Telegram / email). | Trả lời ngắn |

---

## Cách đếm — ghi TRƯỚC khi đọc kết quả (chép sang `evidence/hypothesis.md`)

- **Mẫu hợp lệ (n):** phiếu có A1 ≠ "Trên 2 năm" **và** A3 ≠ "Không dùng", người trả lời **không phải** thành viên nhóm. Senior (Phần D) đếm riêng, không cộng vào n.
- **Giả thuyết đạt** nếu: **≥40% của n** chọn B4 = "Có, ít nhất 1 đoạn". "Không chắc" **không** tính là gặp pain (báo riêng số này).
- **Số kiểm lại:** % có B5 ≥ 1 lần hoặc B7 ≥ 1 lần (đã thực sự bị hỏi / trả lại). So với kết quả thử nghiệm "giải thích lại" (x/N đoạn giải thích đúng).
- **Số cho impact:** trung vị số lần / tháng = trung vị của max(B5, B7) trên người gặp pain ("4 lần trở lên" tính 4, "Không nhớ" bỏ) · thời gian mỗi lần = trung vị B8 (lấy điểm giữa khoảng: 7,5 / 22,5 / 45 / 90 / 150 phút) · phía senior = trung vị D3.
- **Số cho persona:** task / tháng = trung vị B1 × 4, tách theo A2 (sinh viên năm 3–4 → `sinh_vien_do_an`, fresher / junior → `junior_di_lam`, tự học → `tu_hoc_chuyen_nganh`); tỉ lệ persona = tỉ lệ A2 trong n.
- Dưới ~10 người một nhóm thì chỉ ghi x/n, không ghi %.

## Lưu kết quả

- Xuất Google Sheets → CSV, **xoá cột E1, D5 và cột thời gian nếu nhận ra người**, lưu `evidence/survey/results.csv`. Bản gốc **không** commit.
- Số chính + ≥3 câu B10 / D4 nguyên văn (đã bỏ tên công ty, tên người) → `evidence/summary.md`.
- Câu trả lời Phần C → `eval/real_cases.csv` (xem lưu ý ở Phần C), chạy `python eval/import_real_cases.py` để kiểm, **trước lượt eval 1**.

## Tạo form tự động bằng Apps Script (2 phút)

1. Mở https://script.google.com → **New project**.
2. Xoá code mẫu, dán toàn bộ nội dung [`create_form.gs`](create_form.gs) → **Save**.
3. Chọn hàm `createCodeOwnSurvey` → **Run** → cấp quyền (tài khoản Google của bạn).
4. Xem **Execution log**: có link sửa form và link gửi đi. Mở link sửa, kiểm lại rẽ nhánh bằng nút **Preview**.
5. Trong form: **Settings → Responses** → tắt *Collect email addresses*; nút **Responses → Link to Sheets** để có bảng kết quả.
