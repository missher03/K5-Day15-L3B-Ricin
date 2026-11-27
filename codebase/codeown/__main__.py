"""CLI lõi CodeOwn (task.md mục 0.6).

Ba kiểu in (lỗi luôn có mã thoát ≠ 0):
  (mặc định)  chữ dễ đọc cho người
  --json      MỘT dòng JSON — hợp đồng cho extension; lỗi → {"error": ...}
  --jsonl     mỗi bản ghi một dòng JSON (attribute: mỗi dòng code một dòng; log: mỗi sự kiện một dòng)

  python -m codeown init --repo <path> [--tools claude_code,cursor] [--rules-only]
  python -m codeown hook --tool=<tên>            (đọc JSON stdin, không in gì)
  python -m codeown status [--task <id>] --json
  python -m codeown attribute [--task <id>] --json
  python -m codeown task new [--name <tên>] --json
  python -m codeown log [--task <id>] [--last N] [--jsonl]   xem sự kiện đã ghi
  python -m codeown check start|answer · reflect · ledger save · done   (phần B: codeown/check.py, done.py)

Chạy từ thư mục codebase/, hoặc: python codebase/codeown_cli.py <lệnh>.
"""
import argparse
import json
import os
import sys

if __package__ in (None, ""):  # chạy thẳng file này
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = "codeown"  # noqa: A001

from codeown import events as E  # noqa: E402
from codeown import pretty  # noqa: E402

B_CMDS = {"check", "reflect", "ledger", "done"}
FMT = {"mode": "text"}


def _utf8_stdout():
    # Windows: stdout qua pipe mặc định cp1252 → chữ Việt bị lỗi / UnicodeEncodeError khi extension đọc
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def _line(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")


def _out(obj, code=0, text=None, rows=None):
    """text: hàm in cho người · rows: danh sách bản ghi cho --jsonl (mặc định: chính obj)."""
    mode = FMT["mode"]
    if mode == "json" or (mode == "text" and (text is None or "error" in obj)):
        if mode == "text" and "error" in obj:
            sys.stdout.write("Lỗi: %s\n" % obj["error"])
        else:
            _line(obj)
    elif mode == "jsonl":
        for row in (rows if rows is not None else [obj]):
            _line(row)
    else:
        sys.stdout.write(text(obj) + "\n")
    return code


def _attr_rows(r):
    head = {k: r.get(k) for k in ("task_id", "di", "stats", "features")}
    return [dict(head, kind="summary")] + [dict(ln, kind="line") for ln in r.get("lines") or []]


def _parser():
    p = argparse.ArgumentParser(prog="codeown", description="CodeOwn — lõi Python")
    p.add_argument("--json", action="store_true", help="in một dòng JSON (cho extension)")
    p.add_argument("--jsonl", action="store_true", help="mỗi bản ghi một dòng JSON")
    sub = p.add_subparsers(dest="cmd")

    def common(sp):
        sp.add_argument("--repo", default=None, help="thư mục repo (mặc định: repo chứa thư mục hiện tại)")
        sp.add_argument("--json", action="store_true", default=argparse.SUPPRESS)
        sp.add_argument("--jsonl", action="store_true", default=argparse.SUPPRESS)
        return sp

    sp = common(sub.add_parser("init"))
    sp.add_argument("--tools", default="claude_code")
    sp.add_argument("--rules-only", action="store_true")

    sp = common(sub.add_parser("hook"))
    sp.add_argument("--tool", required=True)

    sp = common(sub.add_parser("status"))
    sp.add_argument("--task", default=None)
    sp.add_argument("--no-record", action="store_true", help="không ghi sự kiện nudge (để xem thử)")

    sp = common(sub.add_parser("attribute"))
    sp.add_argument("--task", default=None)

    sp = common(sub.add_parser("task"))
    sp.add_argument("action", choices=["new", "show"])
    sp.add_argument("--name", default=None)

    sp = common(sub.add_parser("log"))
    sp.add_argument("--task", default=None, help="mặc định: task hiện tại · 'all' = mọi task")
    sp.add_argument("--last", type=int, default=30)

    for name in B_CMDS:  # tham số còn lại (start --task ...) đi nguyên thứ tự sang main() của B
        common(sub.add_parser(name, add_help=False))
    return p


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = _parser()
    args, extra = parser.parse_known_args(argv)  # lệnh B nhận --task ... qua extra
    if extra and args.cmd not in B_CMDS:
        parser.error("không hiểu: %s" % " ".join(extra))
    FMT["mode"] = "json" if "--json" in argv else "jsonl" if "--jsonl" in argv else "text"
    if not args.cmd:
        return _out({"error": "thiếu lệnh — xem: python -m codeown -h"}, 2)
    if args.cmd == "hook":
        from codeown.hook import run
        run(args.tool, repo=os.path.abspath(args.repo) if args.repo else None)
        return 0
    _utf8_stdout()
    repo = E.find_repo(args.repo)
    try:
        if args.cmd == "init":
            from codeown.install import init
            tools = [t.strip() for t in args.tools.split(",") if t.strip()]
            return _out(init(repo, tools, args.rules_only), text=pretty.kv)
        if args.cmd == "status":
            from codeown.monitor import status
            return _out(status(repo, args.task, record_nudge=not args.no_record), text=pretty.status)
        if args.cmd == "attribute":
            from codeown.monitor import attribution_report
            r = attribution_report(repo, args.task)
            return _out(r, text=pretty.attribute, rows=_attr_rows(r))
        if args.cmd == "task":
            if args.action == "new":
                return _out(E.new_task(repo, args.name), text=pretty.kv)
            return _out(dict(E.load_state(repo), task_id=E.current_task_id(repo)), text=pretty.kv)
        if args.cmd == "log":
            tid = None if args.task == "all" else (args.task or E.current_task_id(repo))
            evs = E.read_events(repo, tid)[-args.last:] if args.last > 0 else E.read_events(repo, tid)
            return _out({"task_id": tid, "events": evs}, rows=evs,
                        text=lambda r: "\n".join(pretty.event(e) for e in r["events"]) or "(chưa có sự kiện)")
        if args.cmd in B_CMDS:
            os.chdir(repo)  # lệnh của B dùng đường dẫn .codeown/ tương đối
            from codeown.check import main as check_main
            from codeown.done import main as done_main
            try:
                return done_main(extra) if args.cmd == "done" else check_main([args.cmd] + extra)
            except SystemExit as exc:  # argparse của B: sai tham số → vẫn trả {"error"} (hợp đồng 0.6)
                if not exc.code:
                    return 0
                return _out({"error": "sai tham số cho lệnh %s — xem: python -m codeown %s -h" % (args.cmd, args.cmd)}, 2)
    except Exception as exc:  # noqa: BLE001
        return _out({"error": "%s: %s" % (type(exc).__name__, exc)}, 1)
    return _out({"error": "không hiểu lệnh"}, 2)


if __name__ == "__main__":
    sys.exit(main())
