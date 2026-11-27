# `call_model` nhận thêm tầng model và schema

Luồng CodeOwn cần hai tầng model (nhỏ cho Grader, mạnh cho Examiner / Reflector / giám khảo thứ hai), còn `codebase/ai.py` của khung chỉ có `call_model(system, user)` đọc một `MODEL_NAME`. Ta sửa tối thiểu thành `call_model(system, user, model=None, schema=None)`: `model` ∈ `"small"` / `"strong"` map qua `CODEOWN_MODEL_SMALL` / `CODEOWN_MODEL_STRONG`, khoá `"model"` trả đúng tên model đã gọi để `simulate` tính giá theo từng model. Mọi lần gọi vẫn đi qua `@model_call` nên khung vẫn đếm token.

**Considered Options:** chạy hai process với hai `.env` (không trộn được hai model trong một task); viết hàm gọi model riêng trong `codeown/` (lọt khỏi hợp đồng đếm token, eval mất cột token).

**Consequences:** task.md §0.1 ghi `ai.py` "không sửa" là sai với AGENTS.md; `ai.py` thuộc phần C, nên thay đổi này cần C đồng ý trước khi merge.
