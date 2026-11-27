"""Examiner (AI 2): chọn đoạn code bằng luật, rồi model mạnh đặt 2–5 câu hỏi bám `file:dòng` + rubric ẩn.

Đầu vào duy nhất: danh sách `lines` của hợp đồng 0.3 [{file, line, code, label}] (chỉ dòng thêm mới).
"""
import os
import re

from tracing import note

from . import llm
from .ledger import norm_concept

DOC_EXTS = (".md", ".txt", ".rst", ".json", ".yaml", ".yml", ".toml", ".cfg", ".ini")
MAX_SNIPPETS = 5
MAX_SPAN = 15
# shortcut: A bỏ dòng trống khỏi `lines`, nên coi khoảng hở ≤3 dòng vẫn là một đoạn liền; đổi khi 0.3 giữ dòng trống.
HUNK_GAP = 3

# Bảng điểm chọn đoạn (Q14) *(tự ước tính)*, chỉnh sau lượt 1.
_BRANCH = re.compile(r"\b(if|elif|else|try|except|catch|finally|raise|throw)\b")
_RISKY = re.compile(r"(sql|select |insert |cursor|execute|session|token|password|passwd|hash|auth|login|jwt|"
                    r"open\(|os\.path|pathlib|requests\.|urllib|fetch\(|socket|http)", re.IGNORECASE)
SCORES = [
    (3, lambda h: any(l["label"] == "ai_giu_nguyen" for l in h)),
    (2, lambda h: any(_BRANCH.search(l["code"]) for l in h)),
    (2, lambda h: any(_RISKY.search(l["code"]) for l in h)),
    (1, lambda h: any(re.match(r"\s*(import|from)\s", l["code"]) for l in h)),
    (1, lambda h: len(h) > 15),
]

QUESTION = llm.strict({
    "file": {"type": "string"},
    "lines": {"type": "array", "items": {"type": "integer"}},
    "concept": {"type": "string"},
    "question": {"type": "string"},
    "rubric_hidden": {"type": "string"},
})
SCHEMA = llm.strict({"questions": {"type": "array", "items": QUESTION}})


_TRIVIAL = re.compile(r"^[\s()\[\]{};,]*$")


def _shape(code):
    """Dáng của dòng: bỏ khoảng trắng, đổi ' thành ", thay mọi tên bằng x — để nhận diff chỉ đổi định dạng / tên."""
    return re.sub(r"[A-Za-z_]\w*", "x", re.sub(r"\s+", "", code.replace("'", '"')))


def only_format_or_rename(lines, removed):
    """True khi dòng thêm và dòng xoá có cùng tập dáng: chỉ đổi định dạng / tên biến, logic không đổi (M05)."""
    added = [l["code"] for l in lines if not _TRIVIAL.match(l["code"])]
    gone = [l["code"] for l in removed or () if not _TRIVIAL.match(l["code"])]
    return bool(added) and bool(gone) and sorted(map(_shape, added)) == sorted(map(_shape, gone))


def should_open(lines, removed=()):
    """None nếu mở Check, ngược lại là lý do không mở (luật design §5.3).
    removed: các dòng bị xoá [{file, code}] — có thì nhận ra diff chỉ đổi định dạng / tên."""
    if not lines:
        return "diff không có dòng mới"
    if all(os.path.splitext(l["file"])[1].lower() in DOC_EXTS for l in lines):
        return "diff chỉ đổi docs / config"
    if only_format_or_rename(lines, removed):
        return "diff chỉ đổi định dạng / tên"
    ai = sum(1 for l in lines if l["label"] != "nguoi_viet")
    if ai >= 20 or ai / len(lines) >= 0.3:
        return None
    return "dưới ngưỡng: %d dòng AI (%.0f%% diff)" % (ai, 100.0 * ai / len(lines))


def n_questions(di):
    return 2 if di < 40 else 3 if di <= 70 else 5


def hunks(lines):
    """Gom dòng thành các đoạn liền theo file."""
    out = []
    for l in sorted(lines, key=lambda l: (l["file"], l["line"])):
        if out and out[-1][-1]["file"] == l["file"] and l["line"] - out[-1][-1]["line"] <= HUNK_GAP:
            out[-1].append(l)
        else:
            out.append([l])
    return out


def score(hunk):
    return sum(points for points, rule in SCORES if rule(hunk))


def select_snippets(lines):
    candidates = [h for h in hunks(lines) if any(l["label"] != "nguoi_viet" for l in h)]
    return sorted(candidates, key=score, reverse=True)[:MAX_SNIPPETS]


def validate(question, snippets):
    """Lỗi `file:dòng` của một câu hỏi (Q13), rỗng nếu hợp lệ."""
    span = question.get("lines") or []
    if len(span) != 2 or span[0] > span[1]:
        return "lines phải là [dòng đầu, dòng cuối]"
    start, end = span
    if end - start > MAX_SPAN:
        return "đoạn %d–%d dài quá %d dòng" % (start, end, MAX_SPAN)
    for h in snippets:
        numbers = {l["line"] for l in h if l["file"] == question.get("file")}
        if start in numbers and end in numbers:
            return ""
    return "%s:%d–%d không nằm trọn trong một đoạn code mới đã cho" % (question.get("file"), start, end)


def _render(snippets, task_intent, dont_ask, ask_first):
    parts = ["Mục đích task: %s" % (task_intent or "chưa rõ")]
    for i, h in enumerate(snippets, 1):
        parts.append("Đoạn %d:\n%s" % (i, "\n".join("%s:%d [%s] %s" % (l["file"], l["line"], l["label"], l["code"])
                                                    for l in h)))
    parts.append("ĐỪNG HỎI: %s" % (", ".join(sorted(dont_ask)) or "(không có)"))
    parts.append("HỎI TRƯỚC: %s" % (", ".join(sorted(ask_first)) or "(không có)"))
    return "\n\n".join(parts)


def _fake(snippets, n):
    qs = []
    for h in snippets[:n]:
        qs.append({"file": h[0]["file"], "lines": [h[0]["line"], h[min(len(h), MAX_SPAN) - 1]["line"]],
                   "concept": "khái niệm giả %d" % (len(qs) + 1),
                   "question": "[câu hỏi giả] Đoạn này làm gì, và nếu bỏ nó đi thì sao?",
                   "rubric_hidden": "[rubric giả]"})
    return {"questions": qs, "fake": True}


def examine(lines, di, task_intent=None, dont_ask=(), ask_first=(), task_id=None, removed=()):
    """→ {"task_id", "questions": [{qid, file, lines, concept, question, rubric_hidden}]} hoặc {"task_id", "skip"}."""
    reason = should_open(lines, removed)
    if reason:
        note("không mở Check: " + reason)
        return {"task_id": task_id, "skip": reason}
    n = n_questions(di)
    snippets = select_snippets(lines)
    dont_ask = {norm_concept(c) for c in dont_ask}
    fence = llm.new_fence()
    system = llm.load_prompt("examiner", N=n, FENCE=fence)
    user = llm.fenced(fence, _render(snippets, task_intent, dont_ask, {norm_concept(c) for c in ask_first}))

    def check(data):
        return ["câu %d: %s" % (i, err) for i, q in enumerate(data.get("questions", []), 1)
                for err in [validate(q, snippets)] if err]

    data, errors = llm.ask_json(system, user, "strong", SCHEMA, "medium", check, _fake(snippets, n))
    if errors:
        note("bỏ câu sai sau khi hỏi lại: " + "; ".join(errors))
    kept = [q for q in (data or {}).get("questions", [])
            if not validate(q, snippets) and norm_concept(q["concept"]) not in dont_ask][:n]
    if len(kept) < n:
        note("chỉ còn %d/%d câu hợp lệ, không bịa thêm" % (len(kept), n))
    result = {"task_id": task_id,
              "questions": [dict(q, qid="q%d" % i) for i, q in enumerate(kept, 1)]}
    if data and data.get("fake"):
        result["fake"] = True
    return result
