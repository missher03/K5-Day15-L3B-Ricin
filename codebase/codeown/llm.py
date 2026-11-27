"""Phần chung của Examiner / Grader / Reflector: nạp prompt, rào dữ liệu (ADR 0004), gọi model trả JSON."""
import json
import os
import re
import secrets

from ai import call_model

PROMPTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")
_FENCE_LIKE = re.compile(r"<<<\s*DATA\w*|DATA\w*\s*>>>", re.IGNORECASE)


def new_fence():
    return "DATA_" + secrets.token_hex(2)


def load_prompt(name, **values):
    with open(os.path.join(PROMPTS, name + ".md"), encoding="utf-8") as f:
        text = f.read()
    for key, value in values.items():
        text = text.replace("{{%s}}" % key, str(value))
    return text


def fenced(fence, data):
    """Bọc dữ liệu không tin được trong rào; xoá mọi chuỗi giống rào có sẵn trong dữ liệu."""
    return "<<<%s\n%s\n%s>>>" % (fence, _FENCE_LIKE.sub("", data), fence)


def ask_json(system, user, model, schema, effort, check, fake):
    """Gọi model, parse JSON, chạy check(data) -> [lỗi]. Có lỗi thì gửi lại 1 lần kèm danh sách lỗi.

    Trả (data, lỗi còn lại). Model fake → dùng `fake` nhưng vẫn chạy check. data là None nếu không parse được.
    """
    data, errors = None, []
    for _ in range(2):
        prompt = user if not errors else (
            user + "\n\nOutput lần trước có lỗi, sửa rồi trả lại toàn bộ JSON:\n- " + "\n- ".join(errors))
        r = call_model(system, prompt, model=model, schema=schema, effort=effort)
        if r["model"] == "fake":
            return fake, check(fake)
        try:
            data = json.loads(r["text"])
        except ValueError as e:
            data, errors = None, ["không phải JSON hợp lệ: %s" % e]
            continue
        errors = check(data)
        if not errors:
            break
    return data, errors


def strict(properties):
    """Schema object mà structured outputs đòi: mọi trường bắt buộc, không thêm trường."""
    return {"type": "object", "properties": properties, "required": list(properties),
            "additionalProperties": False}
