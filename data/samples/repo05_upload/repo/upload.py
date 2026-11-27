import os
import uuid

UPLOAD_DIR = os.path.abspath("uploads")
ALLOWED = {".png", ".jpg", ".jpeg", ".pdf"}
MAX_BYTES = 5 * 1024 * 1024


def save_upload(filename: str, data: bytes) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED:
        raise ValueError("định dạng không cho phép")
    if len(data) > MAX_BYTES:
        raise ValueError("file vượt quá 5MB")
    safe_name = uuid.uuid4().hex + ext
    path = os.path.join(UPLOAD_DIR, safe_name)
    if not os.path.abspath(path).startswith(UPLOAD_DIR + os.sep):
        raise ValueError("đường dẫn không hợp lệ")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return safe_name
