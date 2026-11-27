"""In kết quả cho người đọc (mặc định của CLI khi không có --json / --jsonl)."""

LABEL_VI = {"ai_giu_nguyen": "AI, giữ nguyên", "ai_da_sua": "AI, bạn đã sửa", "nguoi_viet": "bạn tự viết"}
MARK = {"ai_giu_nguyen": "AI ", "ai_da_sua": "AI*", "nguoi_viet": "   "}
EVENT_VI = {"prompt": "prompt", "ai_edit": "AI sửa file", "ai_bash": "AI chạy lệnh", "ai_turn_end": "AI xong lượt",
            "commit": "commit", "nudge": "nhắc", "manual_mark": "đánh dấu tay"}


def _stats(st):
    return " · ".join("%s %d" % (LABEL_VI[k], st.get(k, 0)) for k in LABEL_VI)


def _feats(f):
    if not f:
        return "chưa có dữ liệu"
    f4 = "—" if f.get("f4_sec") is None else "%ss" % f["f4_sec"]
    txt = "f1 %.2f · f2 %.2f · f3 %s · f4 %s · f5 %s" % (f.get("f1", 0), f.get("f2", 0), f.get("f3", 0), f4,
                                                       f.get("f5", 0))
    if f.get("missing"):
        txt += "  (thiếu: %s)" % ", ".join(f["missing"])
    return txt


def status(r):
    lines = ["Task   %s" % r.get("task_id"),
             "DI     %s" % ("— (chưa có sự kiện)" if r.get("di") is None else r["di"]),
             "Dòng   %s" % _stats(r.get("stats") or {}),
             "Đo     %s" % _feats(r.get("features"))]
    if r.get("ignored_files"):
        lines.append("Bỏ qua %s" % ", ".join(r["ignored_files"]))
    n = r.get("pending_nudge")
    lines.append("Nhắc   %s" % (n["message"] if n else "không"))
    return "\n".join(lines)


def attribute(r):
    out = [status({k: r.get(k) for k in ("task_id", "di", "stats", "features", "ignored_files")}).rsplit("\n", 1)[0], ""]
    cur = None
    for ln in r.get("lines") or []:
        if ln["file"] != cur:
            cur = ln["file"]
            out.append("── %s" % cur)
        out.append("%5d %s │ %s" % (ln["line"], MARK[ln["label"]], ln["code"].rstrip()))
    out.append("")
    out.append("AI  = AI viết, giữ nguyên · AI* = AI viết, bạn đã sửa · trống = bạn tự viết")
    return "\n".join(out)


def event(e):
    t = (e.get("ts") or "")[11:19]
    kind = EVENT_VI.get(e.get("event"), e.get("event"))
    meta = e.get("meta") or {}
    if e.get("event") == "prompt":
        lab = meta.get("label") or meta.get("label_rules") or ""
        body = "[%s] %s" % (lab, (e.get("prompt") or "").replace("\n", " ⏎ ")[:100])
    elif e.get("event") == "ai_edit":
        body = "%s (+%d dòng)" % (e.get("file"), len(e.get("line_hashes") or []))
    elif e.get("event") == "ai_bash":
        body = (meta.get("command") or "")[:100]
    elif e.get("event") == "commit":
        body = "%s %s" % ((e.get("commit") or "")[:8], meta.get("message", ""))
    elif e.get("event") == "nudge":
        body = meta.get("rule", "")
    else:
        body = ""
    return "%s  %-6s %-13s %s" % (t, e.get("tool") or "", kind, body)


def kv(d):
    return "\n".join("%-12s %s" % (k, v) for k, v in d.items())
