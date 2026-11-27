"""Grader (AI 3): luật code trước model → model nhỏ chấm → giám khảo thứ hai → guard chống lộ đáp án.

Hàm thuần: không đọc / ghi file. Lớp CLI giữ kết quả phiên và tăng `round`.
Kết quả theo hợp đồng 0.5 + `status` (ADR 0002).
"""
import os
import re

from tracing import note

from . import llm
from .guard import leaks_answer, safe_hint

LABELS = ["hieu", "mot_phan", "chua_hieu"]
MAX_ROUND = 2
_DONT_KNOW = re.compile(r"^(tôi |mình |em |anh |chị )?(không|ko|k|chả|chưa)\s*(biết|rõ|hiểu)( ạ| nữa)?$")
SCHEMA = llm.strict({
    "label": {"type": "string", "enum": LABELS},
    "confidence": {"type": "number"},
    "missing_concept": {"type": "string"},
    "hint": {"type": "string"},
    "follow_up": {"type": "string"},
})
FAKE = {"label": "mot_phan", "confidence": 0.5, "missing_concept": "khái niệm giả",
        "hint": "[gợi ý giả] Thử đọc lại đoạn này.", "follow_up": "[câu hỏi tiếp giả] Nếu bỏ dòng này thì sao?",
        "fake": True}


class GradeError(RuntimeError):
    """Model trả output sai schema cả sau lần thử lại."""


def _norm_line(s):
    return " ".join(s.split())


def is_dont_know(answer):
    s = re.sub(r"[^\w\s]", "", (answer or "").lower()).strip()
    return len((answer or "").strip()) < 15 or bool(_DONT_KNOW.match(s))


def is_pasted(answer, diff_codes):
    """≥2 dòng và ≥80% số dòng không rỗng của câu trả lời có nguyên văn trong diff (Q17)."""
    diff = {_norm_line(c) for c in diff_codes if c.strip()}
    rows = [_norm_line(r) for r in (answer or "").splitlines() if r.strip()]
    hits = sum(1 for r in rows if r in diff)
    return hits >= 2 and hits >= 0.8 * len(rows)


def _check(data):
    errors = []
    if data.get("label") not in LABELS:
        errors.append("label phải là một trong %s" % LABELS)
    c = data.get("confidence")
    if not isinstance(c, (int, float)) or isinstance(c, bool) or not 0 <= c <= 1:
        errors.append("confidence phải là số trong [0, 1]")
    return errors


def _judge(model, question, rubric, answer):
    fence = llm.new_fence()
    user = llm.fenced(fence, "Câu hỏi: %s\n\nRubric ẩn: %s\n\nCâu trả lời của người dùng:\n%s"
                      % (question, rubric, answer))
    return llm.ask_json(llm.load_prompt("grader", FENCE=fence), user, model, SCHEMA, "low", _check, FAKE)


def _second_judge_on():
    return os.environ.get("CODEOWN_SECOND_JUDGE", "1") == "1"


def grade(question, rubric, answer, round=1, diff_codes=()):
    """question: dict 0.4 (qid, question, concept, lines). diff_codes: code các dòng mới của task."""
    concept, span = question.get("concept"), question.get("lines")
    base = {"qid": question.get("qid"), "label": None, "confidence": None, "missing_concept": None,
            "hint": None, "follow_up": None, "round": round, "final": False}

    if is_dont_know(answer):
        return dict(base, status="need_retry", hint=safe_hint(concept, span))
    if is_pasted(answer, diff_codes):
        return dict(base, status="need_own_words",
                    hint="Hãy giải thích bằng lời của bạn: đoạn này làm gì và vì sao cần nó, thay vì dán lại code.")

    data, errors = _judge("small", question["question"], rubric, answer)
    if errors:
        raise GradeError("; ".join(errors))
    label, confidence = data["label"], float(data["confidence"])

    if label == "hieu" and confidence < 0.7 and _second_judge_on():
        second, errors = _judge("strong", question["question"], rubric, answer)
        if errors or second["label"] != "hieu":
            note("giám khảo thứ hai không đồng ý (%s) → mot_phan" % ("lỗi output" if errors else second["label"]))
            label = "mot_phan"
            if not errors:  # gợi ý của giám khảo thứ hai khớp với nhãn mới hơn
                data = dict(data, **{k: second[k] for k in ("missing_concept", "hint", "follow_up")})

    result = dict(base, status="graded", label=label, confidence=confidence,
                  final=label == "hieu" or round >= MAX_ROUND)
    if label != "hieu":
        result["missing_concept"] = data.get("missing_concept") or concept
        result["hint"] = data.get("hint") or None
        if label == "mot_phan" and round < MAX_ROUND:
            result["follow_up"] = data.get("follow_up") or safe_hint(result["missing_concept"], span)
    for key in ("hint", "follow_up"):
        if leaks_answer(result[key], rubric):
            note("guard: %s lộ đáp án → thay bằng gợi ý an toàn" % key)
            result[key] = safe_hint(result["missing_concept"], span)
    if data.get("fake"):
        result["fake"] = True
    return result
