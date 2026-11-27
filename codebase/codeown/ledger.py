"""Sổ kiến thức: `.codeown/ledger.jsonl`, mỗi dòng {ts, task_id, concept, label}.

Chỉ ghi khi người dùng bấm Lưu (ADR 0003). Chỉ ghi thêm vào cuối; lưu lại cùng task_id thì
lần lưu sau thay lần trước khi đọc (mọi dòng của một lần lưu có cùng ts), nên Lưu nhiều lần vẫn
cho cùng kết quả.
"""
import datetime
import json
import os
import unicodedata

LEDGER = os.path.join(".codeown", "ledger.jsonl")


def norm_concept(concept):
    return " ".join(unicodedata.normalize("NFC", concept or "").lower().split())


def save(task_id, items, path=LEDGER):
    """items: [{"concept", "label"}]. Trả số dòng đã ghi."""
    ts = datetime.datetime.now().astimezone().isoformat(timespec="microseconds")
    rows = [{"ts": ts, "task_id": task_id, "concept": norm_concept(i["concept"]), "label": i["label"]}
            for i in items if norm_concept(i.get("concept"))]
    if not rows:
        return 0
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return len(rows)


def _tasks(path):
    """Bản lưu cuối của mỗi task, xếp theo thời điểm lưu: [(ts, task_id, [rows])]."""
    if not os.path.exists(path):
        return []
    latest = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            ts, rows = latest.get(r["task_id"], ("", []))
            if r["ts"] > ts:
                latest[r["task_id"]] = (r["ts"], [r])
            elif r["ts"] == ts:
                rows.append(r)
    return sorted((ts, tid, rows) for tid, (ts, rows) in latest.items())


def recent_understood(n=2, path=LEDGER):
    """Khái niệm `hieu` trong n task được lưu gần nhất (đếm theo task, không theo dòng)."""
    return {r["concept"] for _, _, rows in _tasks(path)[-n:] for r in rows if r["label"] == "hieu"}


def weak_concepts(path=LEDGER):
    """Khái niệm từng `chua_hieu` mà về sau chưa được ghi `hieu`."""
    weak = set()
    for _, _, rows in _tasks(path):
        for r in rows:
            if r["label"] == "chua_hieu":
                weak.add(r["concept"])
            elif r["label"] == "hieu":
                weak.discard(r["concept"])
    return weak
