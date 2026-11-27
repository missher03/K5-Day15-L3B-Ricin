"""Ghép các phần của Monitor: gán dòng + DI + nhắc. Extension và agent.py gọi qua đây."""
import os

from . import events as E
from .attribution import attribute, attribute_patch
from .dependence import compute
from .install import load_config
from .nudge import check_nudge

EMPTY_STATS = {"ai_giu_nguyen": 0, "ai_da_sua": 0, "nguoi_viet": 0}


def _mode(repo):
    return "rules" if load_config(repo).get("rules_only") else None


def _label_cache_path(repo):
    return os.path.join(E.codeown_dir(repo), "labels.jsonl")


def label_events(repo, evs, mode=None):
    """Gắn meta.label cho prompt. Cache ở .codeown/labels.jsonl, mỗi dòng {"id", "label", "by"}."""
    from .classifier import classify
    path = _label_cache_path(repo)
    cache = {r.get("id"): r.get("label") for r in E.load_jsonl(path)}
    new_rows = []
    resolved = (mode or os.environ.get("CODEOWN_CLASSIFIER") or "auto").lower()
    for ev in evs:
        if ev.get("event") != "prompt":
            continue
        meta = ev.setdefault("meta", {})
        if meta.get("label"):
            continue
        key = ev.get("id")
        if key not in cache:
            if resolved == "rules" and meta.get("label_rules"):
                cache[key], by = meta["label_rules"], "rules"
            else:
                cache[key], by = classify(ev.get("prompt") or "", mode), resolved
            new_rows.append({"id": key, "label": cache[key], "by": by})
        meta["label"] = cache[key]
    for row in new_rows:
        E.append_jsonl(path, row)
    return evs


def analyze(repo, task_id=None):
    """Mục 0.3 cho task trong repo thật."""
    task_id = task_id or E.current_task_id(repo)
    evs = label_events(repo, E.read_events(repo, task_id), _mode(repo))
    if any(e.get("event") == "commit" for e in evs):
        att = attribute(repo, task_id)
    else:
        att = {"task_id": task_id, "lines": [], "stats": dict(EMPTY_STATS), "ignored_files": []}
    res = compute(evs, att, _mode(repo))
    att["di"], att["features"] = res["di"], res["features"]
    return att, evs


def _public(feats):
    return {k: v for k, v in (feats or {}).items() if k != "prompt_labels"}


def status(repo, task_id=None, record_nudge=True):
    """→ {"task_id", "di", "stats", "features", "pending_nudge"}. Nhắc được ghi lại để giữ 15 phút chờ."""
    att, evs = analyze(repo, task_id)
    nudge = check_nudge(evs, att["di"], att["features"])
    if nudge and record_nudge:
        E.append_event(repo, E.make_event("nudge", tool="codeown", task_id=att["task_id"],
                                          meta={"rule": nudge["rule"], "metric": nudge["metric"]}))
    return {"task_id": att["task_id"], "di": att["di"], "stats": att["stats"],
            "features": _public(att["features"]), "pending_nudge": nudge,
            "ignored_files": att.get("ignored_files", [])}


def write_summary(repo, task_id=None, commit=None):
    """Sau mỗi commit: thêm 1 dòng tóm tắt task vào .codeown/summary.jsonl (dễ đọc lại theo thời gian).
    Chỉ dùng luật cho prompt chưa có nhãn, để commit không phải chờ model."""
    prev = os.environ.get("CODEOWN_CLASSIFIER")
    os.environ["CODEOWN_CLASSIFIER"] = "rules"
    try:
        att, evs = analyze(repo, task_id)
    finally:
        if prev is None:
            os.environ.pop("CODEOWN_CLASSIFIER", None)
        else:
            os.environ["CODEOWN_CLASSIFIER"] = prev
    row = {"ts": E.now_iso(), "task_id": att["task_id"], "commit": commit, "di": att["di"],
           "stats": att["stats"], "features": _public(att["features"]),
           "prompts": sum(1 for e in evs if e.get("event") == "prompt")}
    E.append_jsonl(os.path.join(E.codeown_dir(repo), "summary.jsonl"), row)
    return row


def attribution_report(repo, task_id=None):
    att, _ = analyze(repo, task_id)
    att["features"] = _public(att["features"])
    return att


def analyze_offline(evs, patch=None, task_id=None, mode="rules", now=None):
    """Bản không git, dùng cho eval (agent.py mode=monitor) và test: sự kiện + patch → kết quả + nhắc."""
    att = attribute_patch(patch, evs, task_id) if patch else \
        {"task_id": task_id, "lines": [], "stats": dict(EMPTY_STATS)}
    res = compute(evs, att, mode)
    nudge = check_nudge(evs, res["di"], res["features"], now=now)
    return {"task_id": task_id, "di": res["di"], "stats": att["stats"],
            "features": _public(res["features"]), "pending_nudge": nudge, "lines": att["lines"]}
