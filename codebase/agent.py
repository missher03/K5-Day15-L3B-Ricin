"""Luồng chính của CodeOwn trong bản chạy thử — phần C (Lê Thành Nguyên). Hình dạng: workflow cố định (spec.md §4).

`python run.py`, `python run.py eval`, `python run.py simulate` đều gọi answer(text).

Đầu vào (task.md mục 0.7) — một chuỗi JSON có "mode":
    {"mode": "examine", "diff_id": "repo03_c1"}
    {"mode": "grade", "case_id": "g07", "question": "...", "rubric": "...", "answer": "...", "round": 1}
    {"mode": "monitor", "session_id": "sess12"}
    {"mode": "reflect", "task_id": "repo05_t1"}
    {"mode": "task", "diff_id": "repo03_c1"}     ← thêm cho simulate: chạy trọn một task (monitor → examine →
                                                   grade từng câu bằng câu trả lời giả lập → reflect)
Gõ tay ở `python run.py` cũng được dạng ngắn: `examine repo03_c1`, `monitor sess01`, `reflect repo10_t1`, `task repo01_c1`.

Đầu ra: {"output": "<JSON dạng chuỗi>"} để run_eval.py, người chấm và eval/auto_score.py đọc.

Mỗi nhánh gọi lõi `codebase/codeown/` của A / B nếu module đã có (tools.core). Chưa có thì trả kết quả GIẢ,
có "fake": true, chỉ bằng code tất định, KHÔNG gọi model — lượt eval chạy nhánh giả không được nộp.
Mọi lần gọi model nằm trong lõi và đi qua ai.call_model (task.md mục 0.8).
Agent không bao giờ đọc truth.json (đáp án của bộ câu thử).
"""
import json
import os
import re

import tools
from tools import (compute_dependence, core, get_events, load_meta, read_diff, sample_dir, search_docs,
                   write_ledger)
from tracing import note

MAX_ROUNDS = 2
DOC_EXT = {".md", ".txt", ".rst", ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg"}
SKIP_RE = re.compile(r"^[\s()\[\]{};,]*$")
HELP = {
    "loi": "đầu vào cần là JSON có \"mode\" (examine / grade / monitor / reflect / task) hoặc dạng ngắn \"examine repo03_c1\"",
    "vi_du": ['{"mode": "examine", "diff_id": "repo03_c1"}', '{"mode": "monitor", "session_id": "sess01"}',
              '{"mode": "reflect", "task_id": "repo10_t1"}', "task repo01_c1"],
}


# ================================================================ cửa vào

def answer(text: str) -> dict:
    req = parse_request(text)
    mode = req.get("mode")
    handler = {"examine": do_examine, "grade": do_grade, "monitor": do_monitor,
               "reflect": do_reflect, "task": do_task}.get(mode)
    if handler is None:
        out = dict(HELP, mode=mode)
    else:
        note("mode=%s" % mode)
        out = handler(req)
    return {"output": json.dumps(out, ensure_ascii=False)}


def parse_request(text):
    text = (text or "").strip()
    try:
        req = json.loads(text)
        if isinstance(req, dict):
            return req
    except ValueError:
        pass
    parts = text.split()
    if len(parts) == 2 and parts[0] in ("examine", "monitor", "reflect", "task"):
        key = {"examine": "diff_id", "task": "diff_id", "monitor": "session_id", "reflect": "task_id"}[parts[0]]
        return {"mode": parts[0], key: parts[1]}
    return {"mode": None, "text": text}


def _id(req, *keys):
    for k in keys:
        if req.get(k):
            return str(req[k])
    raise ValueError("thiếu %s trong đầu vào" % " / ".join(keys))


# ================================================================ mục đích task (code, design.md §5.2)

def task_intent(any_id, events=None):
    """Gom từ mô tả task, tên nhánh, commit message, 3 prompt đầu. Không có gì rõ thì "chưa rõ"."""
    meta = load_meta(any_id)
    events = events if events is not None else get_events(any_id)
    prompts = [e["prompt"] for e in events if e.get("event") == "prompt" and e.get("prompt")][:3]
    branch = meta.get("branch") or ""
    vague_branch = branch in ("", "main", "master", "dev")
    vague_msg = (meta.get("commit_message") or "").strip().lower() in ("", "update", "fix", "wip", "sửa", ".")
    clear = bool(meta.get("description")) or not (vague_branch and vague_msg)
    return {"description": meta.get("description") or "", "branch": branch,
            "commit_message": meta.get("commit_message") or "", "first_prompts": prompts,
            "summary": (meta.get("description") or meta.get("commit_message") or "") if clear else "chưa rõ"}


# ================================================================ examine

def do_examine(req):
    diff_id = _id(req, "diff_id", "task_id")
    diff = read_diff(diff_id)
    dep = compute_dependence(diff_id)
    di = dep.get("di") if isinstance(dep, dict) else None
    intent = task_intent(diff_id)
    examiner = core("examiner")
    if examiner is not None:
        ledger_mod = core("ledger")
        recent = ledger_mod.recent_understood(2) if ledger_mod is not None and hasattr(ledger_mod, "recent_understood") else []
        res = examiner.examine(diff["lines"], di, intent, recent)
        res.setdefault("task_id", diff["task_id"])
        res.setdefault("di", di)
        return res
    return fake_examine(diff, di)


def _shape(line):
    """Dáng của dòng sau khi bỏ khoảng trắng, đổi ' thành ", thay mọi tên bằng x — để nhận diff chỉ đổi định dạng / tên."""
    s = re.sub(r"\s+", "", line.replace("'", '"'))
    return re.sub(r"[A-Za-z_]\w*", "x", s)


PRIORITY = [
    (r"password|hash|salt|hmac|token|jwt|auth|verify", "xác thực / mật khẩu"),
    (r"execute|SELECT|UPDATE|DELETE|LIKE|sql", "truy vấn cơ sở dữ liệu"),
    (r"open\(|path|upload|makedirs|csv|encoding", "đọc / ghi file"),
    (r"fetch|request|http|timeout|retry|Abort", "gọi mạng"),
    (r"\btry\b|except|catch|raise|throw|finally", "xử lý lỗi"),
    (r"\bif\b|\bfor\b|while|return", "rẽ nhánh / ca biên"),
]


def fake_examine(diff, di):
    files = diff["files"]
    if files and all(os.path.splitext(f)[1].lower() in DOC_EXT for f in files):
        return {"fake": True, "task_id": diff["task_id"], "skip": "diff chỉ đổi docs / config", "questions": []}
    added = [l for l in diff["lines"] if not SKIP_RE.match(l["code"])]
    removed = [l for l in diff["removed"] if not SKIP_RE.match(l["code"])]
    if removed and sorted(_shape(l["code"]) for l in added) == sorted(_shape(l["code"]) for l in removed):
        return {"fake": True, "task_id": diff["task_id"], "skip": "diff chỉ đổi định dạng / tên", "questions": []}
    n = 3 if di is None else (2 if di < 40 else (3 if di <= 70 else 5))
    cands = []
    for l in added:
        if l.get("label") == "nguoi_viet":
            continue
        for rank, (pat, concept) in enumerate(PRIORITY):
            if re.search(pat, l["code"], re.I):
                cands.append((rank, l, concept))
                break
    cands.sort(key=lambda x: (x[0], x[1]["file"], x[1]["line"]))
    questions, used = [], set()
    for rank, l, concept in cands:
        if len(questions) >= n:
            break
        if (l["file"], l["line"] // 4) in used:
            continue
        used.add((l["file"], l["line"] // 4))
        questions.append({"qid": "q%d" % (len(questions) + 1), "file": l["file"], "lines": [l["line"], l["line"]],
                          "concept": concept,
                          "question": "Dòng %s:%d làm gì, và nếu bỏ dòng này thì chuyện gì xảy ra?" % (l["file"], l["line"])})
    return {"fake": True, "task_id": diff["task_id"], "di": di, "questions": questions}


# ================================================================ grade

ASK_ANSWER = re.compile(r"(viết lại|viết giúp|code giúp|sửa giúp|đáp án|lời giải|cho (tôi|mình|em) (code|xem code))", re.I)


def do_grade(req):
    question, rubric = req.get("question") or "", req.get("rubric") or ""
    ans, rnd = req.get("answer") or "", int(req.get("round") or 1)
    grader = core("grader")
    if grader is not None:
        res = grader.grade(question, rubric, ans, rnd)
    else:
        res = fake_grade(question, ans, rnd)
    res.setdefault("qid", req.get("qid") or req.get("case_id") or "q1")
    res.setdefault("round", rnd)
    return res


def fake_grade(question, ans, rnd):
    base = {"fake": True, "round": rnd, "confidence": 0.0, "missing_concept": None, "follow_up": None}
    if ASK_ANSWER.search(ans):
        docs = search_docs(question)
        return dict(base, label=None, refuse=True, final=False,
                    hint="CodeOwn không viết code hay đưa đáp án thay bạn. Đọc đoạn docs gợi ý rồi tự trả lời câu hỏi.",
                    docs=[d["link"] for d in docs])
    if len(ans.strip()) < 15 or "không biết" in ans.lower():
        return dict(base, label=None, final=False,
                    hint="Gợi ý mức 1: đọc lại đúng dòng được hỏi và thử nói nó chặn trường hợp xấu nào.")
    return dict(base, label="mot_phan", final=rnd >= MAX_ROUNDS,
                hint="(giả) chưa có Grader thật — lõi B chưa nối.")


# ================================================================ monitor

def do_monitor(req):
    sid = _id(req, "session_id", "task_id")
    dep = compute_dependence(sid)
    nudge_mod = core("nudge")
    if dep is None or nudge_mod is None:
        events = get_events(sid)
        return {"fake": True, "session_id": sid, "di": dep.get("di") if isinstance(dep, dict) else None,
                "features": dep.get("features") if isinstance(dep, dict) else None, "nudge": None,
                "n_events": len(events)}
    meta = load_meta(sid)
    return {"session_id": sid, "task_id": meta["task_id"], "di": dep.get("di"), "features": dep.get("features"),
            "nudge": nudge_mod.check_nudge(meta["task_id"])}


# ================================================================ reflect

def do_reflect(req):
    task_id = _id(req, "task_id", "diff_id")
    tools.use_sample(task_id)
    reflector = core("reflector")
    if reflector is not None:
        return reflector.reflect(load_meta(task_id)["task_id"])
    return fake_reflect(task_id, req.get("check_results"))


def fake_reflect(task_id, check_results=None):
    events = get_events(task_id)
    diff = read_diff(task_id)
    intent = task_intent(task_id, events)
    lines, sources = ["# Reflect (giả — lõi B chưa nối)", "", "## Dòng thời gian"], []
    for e in events:
        if e["event"] in ("prompt", "ai_edit", "commit"):
            what = {"prompt": "bạn gửi prompt", "ai_edit": "AI sửa %s (%d dòng)" % (e.get("file"), len(e.get("line_hashes") or [])),
                    "commit": "commit"}[e["event"]]
            lines.append("- %s: %s [log#%s]" % (e["ts"][11:16], what, e["id"]))
            sources.append("log#" + e["id"])
    lines += ["", "## Mục đích task"]
    if intent["summary"] == "chưa rõ":
        lines.append("- Mục đích task là gì? Nhánh, commit message và prompt đều chưa nói rõ.")
    else:
        first = diff["lines"][0] if diff["lines"] else None
        ref = "[file:%s:%d]" % (first["file"], first["line"]) if first else "[log#%s]" % events[0]["id"]
        lines.append("- Commit ghi: \"%s\" %s" % (intent["commit_message"], ref))
    lines += ["", "## Hỏi lại bạn", "- Bạn chọn cách làm này vì lý do gì, có cân nhắc phương án khác không?"]
    return {"fake": True, "task_id": task_id, "markdown": "\n".join(lines), "sources": sources}


# ================================================================ task (cho simulate chi phí)

def do_task(req):
    diff_id = _id(req, "diff_id", "task_id")
    d = sample_dir(diff_id)
    answers = []
    if d and os.path.exists(os.path.join(d, "sim_answers.json")):
        with open(os.path.join(d, "sim_answers.json"), encoding="utf-8") as f:
            answers = json.load(f)
    meta = load_meta(diff_id)
    monitor = do_monitor({"session_id": meta["task_id"]})
    exam = do_examine({"diff_id": diff_id})
    graded = []
    for k, q in enumerate(exam.get("questions") or []):
        ans = answers[k % len(answers)] if answers else "không biết"
        res = do_grade({"qid": q.get("qid"), "question": q.get("question"), "rubric": q.get("rubric_hidden", ""),
                        "answer": ans, "round": 1})
        if res.get("follow_up") and not res.get("final"):
            res = do_grade({"qid": q.get("qid"), "question": res["follow_up"], "rubric": q.get("rubric_hidden", ""),
                            "answer": answers[(k + 1) % len(answers)] if answers else "không biết", "round": 2})
        graded.append(res)
    reflect = do_reflect({"task_id": meta["task_id"], "check_results": graded}) if not exam.get("skip") else None
    drafts = [write_ledger({"task_id": meta["task_id"], "concept": g.get("missing_concept"), "label": g.get("label")})
              for g in graded if g.get("label")]
    fake = any(isinstance(x, dict) and x.get("fake") for x in [monitor, exam, reflect] + graded)
    return {"fake": fake, "task_id": meta["task_id"], "di": monitor.get("di"), "skip": exam.get("skip"),
            "n_questions": len(exam.get("questions") or []), "labels": [g.get("label") for g in graded],
            "ledger_drafts": len(drafts), "reflect_sources": len((reflect or {}).get("sources") or [])}
