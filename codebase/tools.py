"""Công cụ của bài toán — NHÓM VIẾT. Điền ở guide bước 2.2 (thiết kế) và 3.2 (code).

Mỗi công cụ là một hàm Python có @tool. Docstring ghi đúng 4 ý như sơ đồ ở spec.md §4:
    tên · input · output · có tác động ra ngoài không (gửi tin, sửa dữ liệu, chấm điểm…)
Khung tự ghi mỗi lần gọi công cụ vào trace (tên, input, output rút gọn, thời gian, lỗi).

Số công cụ, kiểu công cụ do thiết kế của nhóm quyết định — có bài chỉ cần một công cụ tra cứu.
Công cụ có tác động ra ngoài: KHÔNG tự làm. Trả về bản nháp chờ người duyệt (guide bước 2.2, "chỗ người duyệt").
Dữ liệu công cụ đọc (bài mẫu, thông báo mẫu, lịch…): để trong data/ và mô tả ở data/DATA_CARD.md.
"""
import json
import os

from tracing import tool, TOOLS  # noqa: F401  (TOOLS: danh sách công cụ đã đăng ký, dùng khi viết vòng lặp agent)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSIONS = os.path.join(ROOT, "data", "samples", "sessions")


@tool
def search_example(query: str) -> list:
    """(ví dụ — thay bằng công cụ của nhóm) Tra dữ liệu mẫu theo câu hỏi.
    Input: câu hỏi (str). Output: danh sách đoạn {"code", "text"}. Không tác động ra ngoài."""
    return [{"code": "VD-1", "text": "(ví dụ) đoạn dữ liệu giả — thay bằng dữ liệu thật của bài toán"}]


@tool
def load_session(session_id: str) -> dict:
    """get_events (bản offline cho eval). Input: mã phiên mẫu trong data/samples/sessions/<id>/.
    Output: {"events": [sự kiện theo task.md 0.2], "patch": diff của task hoặc None}. Không tác động ra ngoài."""
    safe = "".join(c for c in session_id if c.isalnum() or c in "-_")
    folder = os.path.join(SESSIONS, safe)
    evs = []
    with open(os.path.join(folder, "events.jsonl"), encoding="utf-8") as f:
        for line in f:
            if line.strip():
                evs.append(json.loads(line))
    patch_path = os.path.join(folder, "diff.patch")
    patch = None
    if os.path.exists(patch_path):
        with open(patch_path, encoding="utf-8") as f:
            patch = f.read()
    return {"events": evs, "patch": patch}
