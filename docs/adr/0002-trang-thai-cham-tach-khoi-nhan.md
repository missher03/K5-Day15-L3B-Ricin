# Trạng thái chấm tách khỏi nhãn hiểu

Hợp đồng 0.5 ban đầu chỉ có `label` ∈ `hieu` / `mot_phan` / `chua_hieu`, nhưng có những vòng hỏi không được chấm: câu trả lời quá ngắn hoặc "không biết", và câu trả lời dán nguyên code. Ta thêm `status` ∈ `graded` / `need_retry` / `need_own_words`. `label` chỉ có giá trị khi `status == "graded"`, các trường hợp còn lại là `null`. Lý do: nếu ép các vòng đó vào `chua_hieu` thì `cham_khop_nguoi` và `bo_sot_chua_hieu` đo sai. "Grader không chắc" vẫn là `mot_phan` kèm `follow_up`, không phải một status riêng.

**Considered Options:** thêm nhãn thứ tư `chua_cham` (trộn hai trục "đã chấm chưa" và "hiểu tới đâu" vào một trường).

**Consequences:** đổi hợp đồng giữa B, D (webview) và C (benchmark Grader).
