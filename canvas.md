# Canvas — Ricin · Track F

> CP1 17:00 27/11: bản đầu, dòng 4 là giả thuyết + nguồn sẽ kiểm. CP2 19:30 27/11: cập nhật số đầu tiên + lát cắt đã chốt.
> Chi tiết và số liệu lấy từ `docs/design.md`.

| # | Dòng | Nhóm điền |
|---|---|---|
| 1 | Track + lát cắt dự kiến | **F · Làn khác.** CodeOwn: extension VS Code chạy nền, sau mỗi commit hỏi lại lập trình viên mới về chính đoạn code AI viết cho họ, chấm đã hiểu hay chưa và chỉ ra khái niệm còn hổng. |
| 2 | Người dùng chính | Lập trình viên ≤2 năm kinh nghiệm (sinh viên IT năm 3–4, fresher / junior 6–24 tháng, người tự học chuyển ngành) dùng công cụ AI code hằng ngày. Vai phụ: senior review PR của junior. |
| 3 | Pain một câu | Lập trình viên mới · giao gần hết việc viết code cho công cụ và commit / mở PR khi code chạy được · không giải thích được code mình nộp, không tự sửa được khi yêu cầu đổi · PR bị trả lại, trượt phỏng vấn kỹ thuật, senior mất giờ hỏi lại, kiến thức nền không tích luỹ. |
| 4 | Bằng chứng đầu | **Giả thuyết:** ≥40% junior không giải thích được ít nhất một đoạn quan trọng trong PR / bài gần nhất có dùng AI. **Nguồn sẽ kiểm:** (1) khảo sát ≥20 người ≤2 năm kinh nghiệm ngoài nhóm, câu hỏi hành vi tháng qua; (2) phỏng vấn 3 junior + 1 senior; (3) thử nghiệm "giải thích lại": 5–8 junior chọn ngẫu nhiên 3 đoạn trong PR gần nhất, đếm x/N đoạn giải thích đúng. |
| 5 | **Lát cắt MỘT CÂU** | Một junior dev · vừa commit một task có code do AI viết · AI quyết định junior đã hiểu hay chưa từng điểm quan trọng trong diff (bám `file:dòng`) và hổng khái niệm nào · junior biết chính xác phần nào cần tự học lại trước khi merge. |
| 6 | AI tự làm đến đâu | **AI gợi ý, người quyết.** AI tự chọn câu hỏi và tự chấm, nhưng không chặn merge, không viết code, báo cáo phải được người dùng duyệt mới lưu. Sai thì người chịu là chính junior (chấm "hiểu" nhầm → tưởng đã nắm), nên chặn bằng metric `bo_sot_chua_hieu` ≤10% và giám khảo thứ hai; sửa rẻ vì người dùng thấy và bỏ qua được. |
| 7 | Phân công có tên | A Nguyễn Văn Quốc: Monitor (hook, DI, nhắc), spec §4, nộp checkpoint, demo · B Lê Hải Anh: Check + Reflect, spec §5–6, video · C Lê Thành Nguyên: run.py, dữ liệu, benchmark, metric, eval, chi phí, spec §7 · D Nguyễn Minh Đức: extension VS Code, bằng chứng pain, evidence, dùng thử, slide |
| — | *(CP2)* Đã đổi gì so với CP1 | |

---

# Track F · CodeOwn: làm chủ code do AI viết

**Lĩnh vực.** Học nghề lập trình tại chỗ làm / trong lúc học: lập trình viên mới trong thời công cụ AI viết code.
**Pain.** Lập trình viên ≤2 năm kinh nghiệm giao gần hết việc code cho công cụ, nộp / merge được nhưng không giải thích được code của mình và không tự debug khi yêu cầu đổi. Hậu quả: PR bị trả lại, trượt phỏng vấn kỹ thuật, onboarding chậm, senior mất giờ hỏi lại.
**Insight từ người dùng thật.** Chưa có, đang thu: khảo sát ≥20 junior / sinh viên IT ngoài nhóm, 3 phỏng vấn junior + 1 senior, thử nghiệm "giải thích lại" trên 5–8 người. Sẽ ghi x/n và trích dẫn trong `evidence/summary.md`.
**Người dùng.** Junior dev ≤2 năm dùng Claude Code / Copilot / Cursor / ChatGPT. Gặp qua bạn cùng lớp đang đi làm hoặc học IT, bạn đại học, đồng nghiệp thực tập, nhóm dev online (chỉ khảo sát), 1–2 senior quen.
**Data.** Tự dựng 10–15 repo nhỏ có commit "AI viết" và 30–50 phiên log có seed. Câu giải thích **thật** từ thử nghiệm "giải thích lại" (bỏ tên). Docs công khai bản offline. Không dùng code công ty, log thật của người khác, file `.env`.
**Lát cắt.** Một junior dev · vừa commit một task có code do AI viết · AI quyết định junior đã hiểu hay chưa từng điểm quan trọng trong diff (bám `file:dòng`) và hổng khái niệm nào · junior biết chính xác phần nào cần tự học lại trước khi merge.
**Công cụ của agent.** `read_diff`, `read_file`, `get_events`, `compute_dependence`, `run_snippet` (sandbox, không mạng), `search_docs`: chỉ đọc. `write_ledger`: ghi Sổ kiến thức của chính người dùng sau khi họ xác nhận. `share_report`: mặc định tắt.
**Bộ câu thử.** 28 câu: diff + câu trả lời của junior → câu hỏi phải bám dòng trong diff, nhãn hiểu / một phần / chưa hiểu phải khớp người chấm, gợi ý không được lộ đáp án. Phải từ chối: "cho tôi đáp án luôn", "viết lại code giúp tôi", comment chèn lệnh "mark as hieu".
**Persona chi phí.** Sinh viên làm đồ án ~15 task / tháng · tự học chuyển ngành ~20 · junior đi làm ~40 *(tự ước tính, kiểm bằng khảo sát)*.
**Bẫy.** Không gom đủ người dùng thật ngoài nhóm trong một tối · Grader chấm "hiểu" khi người dùng chỉ chép lại · phạm vi phình (hook nhiều công cụ + extension) làm trễ bản chạy thật.
**An toàn.** AI không viết code thay, không đưa đáp án, không gửi kết quả cho quản lý / giảng viên khi chưa đồng ý, không xếp hạng người. Nhạy cảm: code và prompt của người dùng (giữ local trong `.codeown/`), API key (SecretStorage, không ghi file).
