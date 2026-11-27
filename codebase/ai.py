"""Nối model — chỗ DUY NHẤT trong bản chạy thử gọi model AI. NHÓM VIẾT phần gọi model thật.

Hợp đồng (giữ nguyên để khung đo được token):
    call_model(system: str, user: str) -> dict với 4 khoá
        "text":       str   chữ model trả về
        "model":      str   tên model đã gọi (để tra giá ở bảng giá model)
        "tokens_in":  int   số token vào, lấy từ trường usage trong phản hồi API — KHÔNG ước lượng
        "tokens_out": int   số token ra, gồm cả token suy luận / suy nghĩ nếu API tính riêng
    @model_call (từ tracing.py) tự ghi mỗi lần gọi vào trace; agent.py gọi call_model bao nhiêu lần
    cũng được, khung tự cộng token.
    Lỗi gọi model (hết lượt, sai key, mất mạng): cứ để exception bay ra — khung ghi lỗi vào cột error.

Chế độ giả (mặc định khi .env chưa có MODEL_PROVIDER, hoặc MODEL_PROVIDER=fake):
    trả một câu giả cố định, model "fake", token 0 — để luồng chạy hết từ trước CP2 (guide bước 3.2).
    Lượt `run.py eval` / `run.py simulate` chạy bằng model giả KHÔNG được tính.

Nối model thật: điền .env (chép từ .env.example), rồi viết nhánh gọi API ở dưới theo docs/connect-model.md
(có ví dụ OpenAI, Claude, model chạy trên máy, và cách nối nhà cung cấp khác). Không dán API key vào file này.
"""
import json
import os
import urllib.error
import urllib.request

from tracing import model_call

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_env(path=os.path.join(ROOT, ".env")):
    """Đọc file .env (KEY=VALUE mỗi dòng) vào biến môi trường, không ghi đè biến đã có. Khung — không cần sửa."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()
MODEL_PROVIDER = (os.environ.get("MODEL_PROVIDER") or "fake").strip().lower()
MODEL_NAME = (os.environ.get("MODEL_NAME") or "").strip()
API_KEY = (os.environ.get("API_KEY") or "").strip()
# CodeOwn cần 2 tầng model (ADR 0001): "small" cho Grader, "strong" cho Examiner / Reflector / giám khảo thứ hai.
TIERS = {"small": os.environ.get("CODEOWN_MODEL_SMALL") or "claude-haiku-5-5",
         "strong": os.environ.get("CODEOWN_MODEL_STRONG") or "claude-sonnet-5-5"}
URL_CLAUDE = "https://api.anthropic.com/v1/messages"


class ModelStopped(RuntimeError):
    """Model dừng bất thường (refusal / max_tokens): output không dùng được."""


def post_json(url, headers, body, timeout=120):
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), method="POST",
                                 headers=dict({"Content-Type": "application/json"}, **headers))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError("HTTP %d: %s" % (e.code, e.read().decode("utf-8", "replace")[:300]))


def call_claude(system, user, name, schema=None, effort=None):
    # Haiku / Sonnet 5.5 từ chối temperature (400) nên không gửi.
    body = {"model": name, "max_tokens": 4000, "system": system or "",
            "messages": [{"role": "user", "content": user}]}
    config = {}
    if schema:
        config["format"] = {"type": "json_schema", "schema": schema}
    if effort:
        config["effort"] = effort
    if config:
        body["output_config"] = config
    data = post_json(URL_CLAUDE, {"x-api-key": API_KEY, "anthropic-version": "2023-06-01"}, body)
    if data.get("stop_reason") in ("refusal", "max_tokens"):
        raise ModelStopped("stop_reason=%s" % data["stop_reason"])
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    u = data["usage"]
    return {"text": text, "tokens_in": u["input_tokens"], "tokens_out": u["output_tokens"]}


@model_call
def call_model(system: str, user: str, model=None, schema=None, effort=None) -> dict:
    """model: None (MODEL_NAME của .env) · "small" · "strong". schema: JSON schema ép output (structured outputs)."""
    if MODEL_PROVIDER == "fake":
        last = (user.strip().splitlines() or [""])[-1]
        return {"text": "[câu trả lời giả — chưa nối model] " + last[:60], "model": "fake", "tokens_in": 0, "tokens_out": 0}
    name = TIERS[model] if model else MODEL_NAME
    if MODEL_PROVIDER == "anthropic":
        r = call_claude(system, user, name, schema, effort)
        return {"text": r["text"], "model": name, "tokens_in": int(r["tokens_in"]), "tokens_out": int(r["tokens_out"])}
    raise NotImplementedError(
        "chưa viết phần gọi model thật cho MODEL_PROVIDER=%s trong codebase/ai.py — xem docs/connect-model.md"
        % MODEL_PROVIDER)
