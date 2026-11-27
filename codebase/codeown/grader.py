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


_STRING = re.compile(r"\"[^\"]*\"|'[^']*'|`[^`]*`")
_VI_LETTER = re.compile(r"[à-ỹÀ-Ỹđ]")
_CODE_START = re.compile(r"^(if|elif|else|for|while|def|class|return|raise|throw|try|except|catch|finally|import|from|"
                         r"const|let|var|function|async|await|with)\b")
_CODE_END = re.compile(r"[:;{}()\[\]]$")


def looks_like_code(row):
    """Một dòng trông như code: bỏ chuỗi trong nháy, không còn chữ tiếng Việt có dấu, và mở đầu bằng từ khoá
    + có dấu code, hoặc kết thúc bằng : ; { } ( ) [ ] và có = hay (."""
    bare = _STRING.sub('""', row.strip())
    if not bare or _VI_LETTER.search(bare):
        return False
    if _CODE_START.match(bare) and re.search(r"[=(){}:;<>\[]", bare):
        return True
    return bool(_CODE_END.search(bare) and re.search(r"[=(]", bare))


def is_pasted(answer, diff_codes):
    """≥2 dòng và ≥80% số dòng không rỗng của câu trả lời có nguyên văn trong diff (Q17).
    Không có diff (vd gọi grade riêng như câu thử G06) → đếm dòng trông như code thay cho dòng trùng diff."""
    diff = {_norm_line(c) for c in diff_codes if c.strip()}
    rows = [_norm_line(r) for r in (answer or "").splitlines() if r.strip()]
    if diff:
        hits = sum(1 for r in rows if r in diff)
    else:
        hits = sum(1 for r in rows if looks_like_code(r))
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


def _vote(question, rubric, answer):
    """Model nhỏ chấm tới CODEOWN_VOTES lần (mặc định 3), dừng khi một nhãn đã quá nửa.
    Lý do: chấm 1 lần đổi nhãn 3/14 câu (21%) giữa hai lần chạy (smoke --variance, 27/11)."""
    n = max(1, int(os.environ.get("CODEOWN_VOTES", "3")))
    votes = []
    for _ in range(n):
        data, errors = _judge("small", question, rubric, answer)
        if errors:
            return data, errors
        votes.append(data)
        labels = [v["label"] for v in votes]
        top = max(labels, key=labels.count)
        if labels.count(top) * 2 > n:
            break
    else:  # ba nhãn khác nhau → lấy mức giữa
        top = "mot_phan"
    if len(votes) > 1:
        note("bỏ phiếu %s → %s" % ("/".join(v["label"] for v in votes), top))
    return next(v for v in votes if v["label"] == top), []


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

    data, errors = _vote(question["question"], rubric, answer)
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
