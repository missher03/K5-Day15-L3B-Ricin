# Khai báo dùng AI

README của nhóm có mục "Dùng AI vào việc gì" (2–3 dòng, bắt buộc). Ghi chi tiết vào bảng dưới đây.

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Code bản chạy thử | Claude Code (Opus 5.5) | Viết `codebase/agent.py`, `codebase/tools.py`, `eval/auto_score.py` | Lê Thành Nguyên đọc lại, chạy `python run.py eval --try 3` và `eval --fake` *(chưa kiểm — điền khi xong)* | C · Lê Thành Nguyên |
| Prompt / thiết kế lời gọi mô hình | | | | |
| Đào data (viết script đếm, gợi ý nhãn) | | | Kiểm tay __ dòng, khớp __ | |
| Rà câu hỏi phỏng vấn / khảo sát | | Chỉ rà câu dẫn dắt | | |
| Viết câu thử (benchmark) | Claude Code (Opus 5.5) | Soạn 28 câu thử, nhãn người chấm và câu trả lời mẫu cho Grader (`source: tu_viet` / `sinh_seed`) | Mỗi câu thử có `source`; người thứ hai thống nhất nhãn G01–G11 *(chưa làm)* | C · Lê Thành Nguyên |
| Sinh data `synthetic` (nếu có) | Claude Code (Opus 5.5) | Viết `data/samples/build_samples.py`, 12 repo mẫu, 40 phiên log, docs offline `data/docs/` | Seed 42 · script tự kiểm luật gán nhãn (0 vi phạm) · kiểm tay __ dòng *(chưa làm)* | C · Lê Thành Nguyên |
| Chấm cột `pass` bằng LLM (nếu có) | | | Kiểm tra thủ công __ câu thử, khớp __/__ | |
| Slide, văn bản | | | | |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).
