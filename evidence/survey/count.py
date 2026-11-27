"""Đếm kết quả khảo sát CodeOwn (form 18 câu đã phát 27/11, xuất ra evidence/survey/results.csv).

    python evidence/survey/count.py evidence/survey/results.csv

Chỉ đọc file, không sửa gì. In số chính cho evidence/summary.md §2 và khối persona cho cost/personas.yaml.
Cột tìm theo số câu ở đầu tiêu đề ("1.", "9.", "11b."…), vì Google Sheets dùng nguyên câu hỏi làm tiêu đề.
Ba nhóm đếm riêng: cả mẫu · không phải senior (câu 1 ≠ "Senior (>3 năm)", đúng người dùng) · senior.
Dưới 10 người thì chỉ ghi x/n, không ghi %. Chỉ dùng thư viện chuẩn.
"""
import csv
import sys
from collections import Counter

SENIOR = "Senior (>3 năm)"
PERSONA = {  # câu 1 → persona trong cost/personas.yaml
    "Sinh viên IT năm 3–4": "sinh_vien_do_an",
    "Fresher / junior đi làm (<2 năm)": "junior_di_lam",
    "Người chuyển ngành": "tu_hoc_chuyen_nganh",
    "Tự học": "tu_hoc_chuyen_nganh",
}
# (nhãn in ra, câu, các lựa chọn tính là "có")
ROWS = [
    ("Dùng AI khi code mỗi ngày", "4", {"Mỗi ngày"}),
    ("≥6/10 lần dùng luôn code AI không sửa", "5", {"6–8", "9–10"}),
    ("  trong đó 9–10/10 lần", "5", {"9–10"}),
    ("30 ngày qua từng nhờ AI làm hộ cả tính năng / bài tập", "6", {"Có vài lần", "Có nhiều lần"}),
    ("  trong đó nhiều lần", "6", {"Có nhiều lần"}),
    ("Gặp lỗi thì dán cho AI luôn", "7", {"Dán lỗi cho AI luôn"}),
    ("Tự tin giải thích ≤50% code AI viết gần nhất", "8", {"0–25%", "26–50%"}),
    ("30 ngày qua từng không giải thích được code mình nộp khi bị hỏi", "9", {"1–3 lần", "Có, hơn 3 lần"}),
    ("  trong đó hơn 3 lần", "9", {"Có, hơn 3 lần"}),
    ("Đổi yêu cầu một chút thì không tự sửa được code AI", "10", {"Có vài lần", "Có nhiều lần"}),
    ("Từng bị review trả lại / trừ điểm / hỏi khó vì code AI không hiểu", "11", {"Có"}),
    ("Lo phụ thuộc AI ≥4/5", "12", {"4", "5"}),
    ("Sẽ dùng công cụ: chắc chắn có", "14", {"Chắc chắn có"}),
    ("Sẽ dùng công cụ: có thể", "14", {"Có thể"}),
    ("Chấp nhận <2 phút mỗi lần trả lời", "16", {"<2 phút"}),
    ("Chấp nhận 2–5 phút", "16", {"2–5 phút"}),
    ("Chấp nhận 5–10 phút", "16", {"5–10 phút"}),
]
MULTI = [("Điều cản dùng công cụ (chọn nhiều)", "15"), ("Đang làm gì để hiểu code AI (chọn nhiều)", "13")]


def col(row, q):
    for k, v in row.items():
        if k and k.split(" ", 1)[0] == q + ".":
            return (v or "").strip()
    raise KeyError("không thấy cột câu %s" % q)


def fmt(x, n):
    return "%d/%d" % (x, n) if n < 10 else "%d/%d (%.0f%%)" % (x, n, 100.0 * x / n)


def main(path):
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    groups = [("Cả mẫu", rows),
              ("Không phải senior", [r for r in rows if col(r, "1") != SENIOR]),
              ("Senior", [r for r in rows if col(r, "1") == SENIOR])]
    print("| Chỉ số | " + " | ".join("%s (n=%d)" % (g, len(rs)) for g, rs in groups) + " |")
    print("|---|" + "---|" * len(groups))
    for label, q, yes in ROWS:
        print("| %s | %s |" % (label, " | ".join(fmt(sum(col(r, q) in yes for r in rs), len(rs)) for _, rs in groups)))
    for label, q in MULTI:
        c = Counter(s.strip() for r in groups[1][1] for s in col(r, q).split(",") if s.strip())
        print("\n%s — không phải senior (n=%d): %s" % (label, len(groups[1][1]),
                                                     " · ".join("%s %d" % kv for kv in c.most_common())))
    print("\nCâu 1 × câu 2 (vai × thời gian code): %s"
          % " · ".join("%s / %s: %d" % (a, b, n) for (a, b), n in
                       Counter((col(r, "1"), col(r, "2")) for r in rows).most_common()))

    target = groups[1][1]
    print("\n# Khối persona cho cost/personas.yaml (share = tỉ lệ câu 1 trong nhóm không phải senior)")
    counts = Counter(PERSONA.get(col(r, "1"), "khac") for r in target)
    for name in ("sinh_vien_do_an", "junior_di_lam", "tu_hoc_chuyen_nganh"):
        print("#  %s: share %.2f (%d/%d)" % (name, counts[name] / len(target), counts[name], len(target)))
    if counts["khac"]:
        print("#  %d phiếu câu 1 không thuộc persona nào" % counts["khac"])
    print("#  uses_per_month: form không hỏi số task / tháng → giữ (tự ước tính)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
