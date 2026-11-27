# Giả thuyết — viết TRƯỚC khi tìm bằng chứng (5 phút, commit ngay)

> Điền ở guide bước 1.1. Ôn lại: ngày 2 · lab ngày 2.
> Viết **trước** khi đọc dòng data đầu tiên hay hỏi người đầu tiên, để không sửa cho khớp kết quả. Kết quả ngược giả thuyết vẫn đủ điểm nếu số là thật.

- Ngày giờ viết: 27/11/2026 18:25 (+07:00)
- Người dùng chính (một vai cụ thể): Lập trình viên mới ≤2 năm kinh nghiệm (sinh viên IT năm 3–4, fresher / junior 6–24 tháng, người tự học chuyển ngành) dùng công cụ AI viết code hằng ngày (Claude Code, Copilot, Cursor, ChatGPT…).
- **Mình nghĩ:** lập trình viên mới gặp khó khi làm chủ và giải thích lại phần code do AI viết trong bài nộp / PR vì quy trình hiện tại (dán yêu cầu → nhận code → chạy được → commit) không có bước bắt đọc lại hay tự kiểm tra hiểu bài, hậu quả là PR bị trả lại, không tự debug được khi yêu cầu đổi, trượt phỏng vấn kỹ thuật và senior tốn thời gian hỏi lại / review lại.
- **Có thể còn cách giải thích khác:**
  1. Junior thật ra hiểu code AI viết, chỉ là lười viết mô tả PR hoặc áp lực deadline nên bỏ qua review.
  2. Họ không ngại việc không hiểu code — miễn code chạy qua test là đủ, nên không thấy đây là pain đáng giải quyết.
  3. Khó khăn chủ yếu nằm ở kiến thức nền chung chứ không liên quan đến việc dùng công cụ AI.
- **Mình đúng nếu thấy:**
  - **Khảo sát (nguồn chính, n ≥ 20 người ngoài nhóm có A1 ≤2 năm KN và A3 có dùng AI):** **≥40% của n** chọn câu **B4 = "Có, ít nhất 1 đoạn"** (có ít nhất một đoạn code quan trọng trong lần nộp gần nhất có dùng AI mà đến giờ vẫn không giải thích được; lựa chọn "Không chắc" không tính vào nhóm gặp pain và báo riêng).
  - **Kiểm lại bằng phỏng vấn (3 junior + 1 senior):** ≥2/3 junior kể được ít nhất 1 lần cụ thể trong 1 tháng qua bị kẹt hoặc không giải thích được code AI đã nộp; senior xác nhận có PR của junior bị hỏi lại / trả lại vì lý do này *(nhóm nhỏ chỉ ghi x/3, không ghi %)*.
  - **Kiểm lại bằng thử nghiệm "giải thích lại" (5–8 junior, 3 đoạn logic ngẫu nhiên / người):** ≥40% số người không giải thích đúng ít nhất 1/3 đoạn code AI viết cho chính họ gần đây *(n < 10 ghi x/n, không ghi %)*.
- **Nguồn sẽ dùng** (≥1 nguồn đạt ngưỡng, guide 1.2): [ ] đào data · [x] phỏng vấn ≥3 · [x] khảo sát ≥20 · [x] thử nghiệm "giải thích lại" (hành vi thật) + 5 trích dẫn công khai — nguồn chính: **khảo sát (≥20)** · nguồn để kiểm lại: **phỏng vấn (3 junior + 1 senior) + thử nghiệm "giải thích lại" (5–8 junior)**.
