"""Reflector (AI 4): báo cáo Reflect một trang, mọi câu khẳng định có mã nguồn kiểm được (Q9, Q20).

Model trả JSON {sections: [{title, claims: [{text, sources}], questions}]}; code kiểm từng mã nguồn,
xoá câu khẳng định không còn nguồn hợp lệ, rồi render markdown.
"""
import os
import re

from tracing import note

from . import llm

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS_DIR = os.path.join("data", "docs")
# shortcut: cắt dữ liệu gửi model để giữ token thấp; nâng khi task thật dài hơn và lượt 1 cho thấy thiếu căn cứ.
MAX_EVENTS, MAX_LINES = 150, 300

CLAIM = llm.strict({"text": {"type": "string"}, "sources": {"type": "array", "items": {"type": "string"}}})
SECTION = llm.strict({"title": {"type": "string"}, "claims": {"type": "array", "items": CLAIM},
                      "questions": {"type": "array", "items": {"type": "string"}}})
SCHEMA = llm.strict({"sections": {"type": "array", "items": SECTION}})
_LINE_REF = re.compile(r"^(?P<file>.+):(?P<start>\d+)(?:-(?P<end>\d+))?$")


def intent_sources(events):
    """[(mã nguồn, chữ)] cho mục đích task: tên nhánh, commit message, 3 prompt đầu."""
    out, branch = [], None
    for e in events:
        if e.get("branch") and not branch:
            branch = e["branch"]
            out.append(("log#" + e["id"], "nhánh: " + branch))
        if e.get("event") == "commit" and (e.get("meta") or {}).get("message"):
            out.append(("log#" + e["id"], "commit message: " + e["meta"]["message"]))
    prompts = [e for e in events if e.get("event") == "prompt" and e.get("prompt")][:3]
    return out + [("log#" + e["id"], "prompt: " + e["prompt"]) for e in prompts]


def docs_files(root=ROOT):
    folder = os.path.join(root, DOCS_DIR)
    if not os.path.isdir(folder):
        return []
    return sorted("%s/%s" % (DOCS_DIR.replace(os.sep, "/"), f) for f in os.listdir(folder) if f.endswith(".md"))


def source_ok(ref, event_ids, diff, root=ROOT):
    """Mã nguồn có thật không: sự kiện có trong log, dòng có trong diff, file docs tồn tại."""
    if ref.startswith("log#"):
        return ref[4:] in event_ids
    if ref.startswith("docs:"):
        path = ref[5:]
        return (path.startswith(DOCS_DIR.replace(os.sep, "/") + "/") and ".." not in path.split("/")
                and os.path.isfile(os.path.join(root, path)))
    m = _LINE_REF.match(ref)
    if not m:
        return False
    numbers = diff.get(m.group("file"), set())
    return int(m.group("start")) in numbers and int(m.group("end") or m.group("start")) in numbers


def _render_data(events, lines, results, intent):
    parts = ["SỰ KIỆN:"]
    for e in events[:MAX_EVENTS]:
        detail = e.get("prompt") or e.get("file") or (e.get("meta") or {}).get("message") or ""
        parts.append("[log#%s] %s %s %s" % (e["id"], e.get("ts", ""), e.get("event", ""), detail))
    parts.append("\nDIFF (dòng mới):")
    parts += ["[%s:%d] [%s] %s" % (l["file"], l["line"], l["label"], l["code"]) for l in lines[:MAX_LINES]]
    parts.append("\nKẾT QUẢ CHECK:")
    for r in results:
        parts.append("[%s:%d-%d] khái niệm: %s · câu hỏi: %s · nhãn cuối: %s · khái niệm hổng: %s" % (
            r["file"], r["lines"][0], r["lines"][1], r["concept"], r["question"], r.get("label") or "chưa chấm",
            r.get("missing_concept") or "-"))
    parts.append("\nMỤC ĐÍCH TASK:")
    parts += ["[%s] %s" % s for s in intent] or ["(không có nguồn)"]
    docs = docs_files()
    if docs:
        parts.append("\nDOCS:")
        parts += ["[docs:%s]" % d for d in docs]
    return "\n".join(parts)


def _fake(events, lines):
    ref = ("log#" + events[0]["id"]) if events else ("%s:%d" % (lines[0]["file"], lines[0]["line"]) if lines else "")
    return {"sections": [{"title": "Bạn đã làm gì", "claims": [{"text": "[báo cáo giả] Task có thay đổi code.",
                                                               "sources": [ref]}],
                          "questions": ["Mục đích task này là gì?"]}], "fake": True}


def render(task_id, sections):
    md, sources = ["# Reflect · %s" % task_id], []
    for s in sections:
        if not s["claims"] and not s["questions"]:
            continue
        md.append("\n## %s" % s["title"])
        for c in s["claims"]:
            md.append("- %s %s" % (c["text"].strip(), " ".join("[%s]" % r for r in c["sources"])))
            sources += [r for r in c["sources"] if r not in sources]
        if s["questions"]:
            md.append("\n**Câu hỏi cho bạn:**")
            md += ["- %s" % q for q in s["questions"]]
    return "\n".join(md) + "\n", sources


def reflect(task_id, events, lines, results):
    """events: sự kiện 0.2 của task · lines: dòng mới 0.3 · results: kết quả từng câu Check (có file, lines,
    concept, question, label, missing_concept; không có rubric). → {"markdown", "sources"}"""
    fence = llm.new_fence()
    system = llm.load_prompt("reflector", FENCE=fence)
    user = llm.fenced(fence, _render_data(events, lines, results, intent_sources(events)))

    def check(data):
        return [] if isinstance(data.get("sections"), list) else ["thiếu sections"]

    data, errors = llm.ask_json(system, user, "strong", SCHEMA, "medium", check, _fake(events, lines))
    if errors:
        raise RuntimeError("Reflector trả output sai schema: " + "; ".join(errors))

    event_ids = {e["id"] for e in events}
    diff = {}
    for l in lines:
        diff.setdefault(l["file"], set()).add(l["line"])
    dropped = 0
    for s in data["sections"]:
        kept = []
        for c in s["claims"]:
            refs = dict.fromkeys(r.strip("[] ") for r in c["sources"])  # bỏ trùng, giữ thứ tự
            c["sources"] = [r for r in refs if source_ok(r, event_ids, diff)]
            if c["sources"]:
                kept.append(c)
            else:
                dropped += 1
        s["claims"] = kept
    if dropped:
        note("xoá %d câu khẳng định không có nguồn hợp lệ" % dropped)
    markdown, sources = render(task_id, data["sections"])
    out = {"markdown": markdown, "sources": sources}
    if data.get("fake"):
        out["fake"] = True
    return out
