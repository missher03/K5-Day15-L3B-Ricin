"""Đưa câu giải thích THẬT (thử nghiệm "giải thích lại" của D) vào bộ câu thử Grader — phần C. Chỉ thư viện chuẩn.

    python eval/import_real_cases.py              kiểm eval/real_cases.csv, in thay đổi sẽ làm (không ghi file)
    python eval/import_real_cases.py --write      thay các câu G.. trong eval/benchmark.csv + eval/bench_truth.json

Cách dùng
  1. Chép eval/real_cases_template.csv thành eval/real_cases.csv, mỗi đoạn code người thử giải thích là một dòng.
  2. Điền đủ cột (xem eval/README.md mục 2):
       thay_cho        id câu sẽ bị thay: G01 … G11 (mỗi id một lần)
       nguon           mã người thử, KHÔNG ghi tên: E1, E2 … (khớp evidence/ của D)
       doan_code       ≤ 12 dòng code người đó giải thích, đã bỏ tên công ty / tên người / key
       cau_hoi         câu đã hỏi người đó ("đoạn này làm gì, bỏ đi thì sao")
       rubric          ý đúng cần có (người chấm viết)
       cau_tra_loi     lời người đó trả lời, đã bỏ tên, được viết lại cho gọn nhưng giữ đúng ý và chỗ sai
       nhan            hieu | mot_phan | chua_hieu | khong_cham (trả lời "không biết" / quá ngắn)
       khai_niem_hong  bắt buộc khi nhan = chua_hieu hoặc mot_phan
       nguoi_cham      hai mã người chấm đã thống nhất nhãn, vd "A,D" (không phải người được thử)
       kho             1 nếu là ca khó (đúng từ khoá sai cơ chế, đúng một nửa…), không thì 0
  3. Chạy không --write để kiểm, rồi --write. Sau đó `python run.py check`.

Chỉ được thay TRƯỚC lượt 1: nếu đã có eval/run-N.csv, script dừng — thay câu thử sau khi đã chạy là xoá câu thử trượt.
"""
import csv
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCH = os.path.join(ROOT, "eval", "benchmark.csv")
TRUTH = os.path.join(ROOT, "eval", "bench_truth.json")
SRC = os.path.join(ROOT, "eval", "real_cases.csv")
COLS = ["thay_cho", "nguon", "doan_code", "cau_hoi", "rubric", "cau_tra_loi", "nhan", "khai_niem_hong", "nguoi_cham", "kho"]
LABELS = {"hieu", "mot_phan", "chua_hieu", "khong_cham"}
PII = [(re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}"), "email"),
       (re.compile(r"(\+84|\b0)[35789]\d{8}\b"), "số điện thoại"),
       (re.compile(r"sk-[A-Za-z0-9]{10,}|ghp_[A-Za-z0-9]{10,}|AKIA[0-9A-Z]{12,}"), "key / token"),
       (re.compile(r"(?i)password\s*=\s*['\"][^'\"]+['\"]"), "mật khẩu")]


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        text = f.read()
    delim = ";" if text.split("\n", 1)[0].count(";") > text.split("\n", 1)[0].count(",") else ","
    r = csv.DictReader(io.StringIO(text), delimiter=delim)
    return [c.strip() for c in r.fieldnames or []], [{(k or "").strip(): (v or "").strip() for k, v in row.items()} for row in r]


def check_rows(rows, bench_ids):
    errs, seen = [], set()
    for k, r in enumerate(rows, start=2):
        where = "dòng %d (%s)" % (k, r.get("thay_cho") or "?")
        for c in ("thay_cho", "nguon", "doan_code", "cau_hoi", "rubric", "cau_tra_loi", "nhan", "nguoi_cham"):
            if not r.get(c):
                errs.append("%s: thiếu cột %s" % (where, c))
        tid = r.get("thay_cho", "")
        if tid and (not re.fullmatch(r"G\d\d", tid) or tid not in bench_ids):
            errs.append("%s: thay_cho phải là một id G01…G11 có trong benchmark" % where)
        if tid in seen:
            errs.append("%s: %s bị thay hai lần" % (where, tid))
        seen.add(tid)
        if r.get("nguon") and not re.fullmatch(r"E\d+", r["nguon"]):
            errs.append("%s: nguon ghi mã người thử dạng E1, E2 … — không ghi tên" % where)
        if r.get("nhan") and r["nhan"] not in LABELS:
            errs.append("%s: nhan phải là một trong %s" % (where, ", ".join(sorted(LABELS))))
        if r.get("nhan") in ("chua_hieu", "mot_phan") and not r.get("khai_niem_hong"):
            errs.append("%s: nhan %s cần khai_niem_hong" % (where, r["nhan"]))
        graders = [g for g in re.split(r"[,; ]+", r.get("nguoi_cham", "")) if g]
        if r.get("nguoi_cham") and len(set(graders)) < 2:
            errs.append("%s: nguoi_cham cần 2 người đã thống nhất nhãn, vd \"A,D\"" % where)
        if len(r.get("doan_code", "").splitlines()) > 12:
            errs.append("%s: doan_code dài quá 12 dòng" % where)
        for pat, what in PII:
            for c in ("doan_code", "cau_hoi", "cau_tra_loi", "rubric"):
                if pat.search(r.get(c, "")):
                    errs.append("%s: cột %s có %s — xoá trước khi đưa vào repo" % (where, c, what))
        if r.get("kho", "0") not in ("0", "1", ""):
            errs.append("%s: kho ghi 0 hoặc 1" % where)
    return errs


def to_case(r):
    label = None if r["nhan"] == "khong_cham" else r["nhan"]
    question = "%s\n<<<CODE\n%s\nCODE>>>" % (r["cau_hoi"], r["doan_code"])
    inp = json.dumps({"mode": "grade", "case_id": r["thay_cho"].lower(), "question": question, "rubric": r["rubric"],
                      "answer": r["cau_tra_loi"], "round": 1}, ensure_ascii=False)
    if label is None:
        expected = "Không chấm; đưa gợi ý mức 1 (không lộ đáp án) và cho trả lời lại"
        crit = "label rỗng / null, final = false, có hint; hint không có code ≥2 dòng, trùng rubric ≤50% từ"
        truth = {"kind": "grade_hint", "label": None, "missing": None, "round": 1, "rubric": r["rubric"]}
    else:
        expected = "Nhãn %s" % label + (" · khái niệm hổng: %s" % r["khai_niem_hong"] if r.get("khai_niem_hong") else "")
        expected += (" · có follow_up hẹp hơn" if label == "mot_phan" else "") + " · gợi ý không lộ đáp án"
        crit = "label = %s; hint / follow_up không có code ≥2 dòng và trùng rubric ≤50%% từ" % label
        if label == "chua_hieu":
            crit += "; missing_concept nêu đúng ý: %s" % r["khai_niem_hong"]
        truth = {"kind": "grade", "label": label, "missing": r.get("khai_niem_hong") or None, "round": 1, "rubric": r["rubric"]}
    truth["source"] = r["nguon"]
    row = {"id": r["thay_cho"], "input": inp, "expected": expected, "pass_criterion": crit,
           "type": "kho" if r.get("kho") == "1" else "thuong",
           "source": "nguoi_dung: %s (thử nghiệm 'giải thích lại', đã bỏ tên; nhãn: %s)" % (r["nguon"], r["nguoi_cham"])}
    return row, truth


def main(args):
    runs = [f for f in os.listdir(os.path.join(ROOT, "eval")) if re.fullmatch(r"run-\d+\.csv", f)]
    if runs:
        sys.exit("Đã có lượt %s — không được thay câu thử sau khi chạy (sẽ thành xoá câu thử trượt). "
                 "Câu thật mới: thêm id mới, không thay." % ", ".join(sorted(runs)))
    if not os.path.exists(SRC):
        sys.exit("Chưa có eval/real_cases.csv — chép từ eval/real_cases_template.csv rồi điền (xem đầu file này).")
    fields, rows = read_csv(SRC)
    missing = [c for c in COLS if c not in fields]
    if missing:
        sys.exit("eval/real_cases.csv thiếu cột: %s" % ", ".join(missing))
    rows = [r for r in rows if any(r.values())]
    bfields, bench = read_csv(BENCH)
    errs = check_rows(rows, {b["id"] for b in bench})
    if errs:
        print("Chưa đưa vào được — sửa các chỗ sau:")
        for e in errs:
            print("  - " + e)
        return 1
    with open(TRUTH, encoding="utf-8") as f:
        truth = json.load(f)
    by_id = {b["id"]: b for b in bench}
    for r in rows:
        row, t = to_case(r)
        print("%s ← %s · nhãn %s · %s" % (row["id"], r["nguon"], r["nhan"], row["type"]))
        by_id[row["id"]].update(row)
        truth[row["id"]] = t
    real = sum(1 for b in bench if b["source"].startswith(("nguoi_dung", "data_that")))
    print("Sau khi thay: %d/%d câu có nguồn người dùng / data thật (cần ≥ %d)." % (real, len(bench), -(-len(bench) // 3)))
    if "--write" not in args:
        print("(Chưa ghi — chạy lại với --write.)")
        return 0
    with open(BENCH, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=bfields)
        w.writeheader()
        w.writerows(bench)
    with open(TRUTH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(truth, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Đã ghi eval/benchmark.csv + eval/bench_truth.json. Tiếp: python run.py check")
    return 0


if __name__ == "__main__":
    for _s in (sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    sys.exit(main(sys.argv[1:]))
