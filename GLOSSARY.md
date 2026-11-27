# CodeOwn

Kiểm xem lập trình viên mới có hiểu code do công cụ AI viết mà họ vừa commit hay không, rồi chỉ ra khái niệm cần học lại.

## Phiên kiểm

**Check**:
Phiên hỏi lại ngay sau commit: hệ thống đặt 2–5 câu hỏi bám đúng `file:dòng` trong diff, người dùng trả lời, từng câu được chấm.
_Avoid_: bài kiểm tra, quiz, exam

**Câu hỏi bám code**:
Câu hỏi trỏ tới một đoạn dòng có trong diff của task, mà đáp án suy ra được từ chính đoạn đó.
_Avoid_: câu hỏi chung, câu hỏi lý thuyết

**Rubric ẩn**:
Ý đúng mà câu trả lời cần có cho một câu hỏi; chỉ Grader thấy, người dùng không bao giờ thấy.
_Avoid_: đáp án, đáp án mẫu

**Vòng hỏi**:
Một lần người dùng trả lời một câu hỏi; mỗi câu hỏi có tối đa 2 vòng.
_Avoid_: lượt, attempt

**Kết quả phiên**:
Bản ghi các câu hỏi, câu trả lời và nhãn của một Check, giữ trên máy người dùng; chưa phải Sổ kiến thức.
_Avoid_: lịch sử, log Check

## Chấm

**Trạng thái chấm**:
Kết cục của một vòng hỏi: đã chấm, cần trả lời lại (quá ngắn / "không biết"), hoặc cần viết lại bằng lời mình (dán code).
_Avoid_: kết quả, outcome

**Nhãn hiểu**:
Mức hiểu của một câu đã chấm: `hieu` · `mot_phan` · `chua_hieu`. Chỉ có khi trạng thái chấm là đã chấm.
_Avoid_: điểm, score, đúng/sai

**Khái niệm hổng**:
Tên khái niệm người dùng chưa nắm, rút ra từ câu trả lời; được phép nêu cho người dùng.
_Avoid_: lỗi sai, missing answer

**Gợi ý**:
Câu dẫn hướng giúp người dùng tự nghĩ ra, không chứa đáp án.
_Avoid_: lời giải, đáp án

**Lộ đáp án**:
Gợi ý hoặc câu hỏi tiếp chứa code ≥2 dòng hoặc phần lớn từ ngữ của rubric ẩn.
_Avoid_: rò rỉ, leak

**Giám khảo thứ hai**:
Model khác chấm lại một câu khi Grader chấm `hieu` mà độ tự tin thấp; không đồng ý thì nhãn hạ xuống `mot_phan`.
_Avoid_: reviewer, judge 2

## Báo cáo và Sổ

**Reflect**:
Báo cáo một trang sau Check về task vừa làm, trong đó mọi câu khẳng định đều có nguồn.
_Avoid_: tổng kết, summary

**Câu khẳng định có nguồn**:
Một câu trong Reflect gắn với ít nhất một nguồn truy được: sự kiện log, `file:dòng` trong diff, hoặc trang docs.
_Avoid_: trích dẫn, citation

**Mã nguồn**:
Chuỗi định danh một nguồn mà Reflect dẫn tới: một sự kiện log, một `file:dòng` trong diff, hoặc một trang docs offline; mỗi mã phải kiểm được là có thật.
_Avoid_: link, reference

**Mục đích task**:
Điều người dùng định làm trong task, rút từ commit message, tên nhánh và vài prompt đầu; các nguồn này có thể mâu thuẫn nhau.
_Avoid_: yêu cầu, requirement

**Sổ kiến thức**:
Ghi chép lâu dài của chính người dùng về các khái niệm đã hiểu / chưa hiểu qua các task; chỉ được ghi khi người dùng bấm Lưu.
_Avoid_: ledger (trong văn bản cho người dùng), lịch sử học

## Đo phụ thuộc

**DI (Dependence Index)**:
Điểm 0–100 đo mức người dùng dựa vào AI trong một task; quyết định số câu hỏi của Check.
_Avoid_: điểm phụ thuộc, AI score

**Nhãn dòng**:
Nguồn gốc một dòng mới trong diff: `ai_giu_nguyen` · `ai_da_sua` · `nguoi_viet`.
_Avoid_: tác giả dòng, attribution label
