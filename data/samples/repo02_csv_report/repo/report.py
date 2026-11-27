import csv
from collections import defaultdict
from decimal import Decimal, InvalidOperation


def load_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = []
        for i, row in enumerate(reader, start=2):
            amount = (row.get("amount") or "").strip()
            if not amount:
                continue
            try:
                row["amount"] = Decimal(amount.replace(",", ""))
            except InvalidOperation:
                raise ValueError(f"dòng {i}: amount không hợp lệ: {amount!r}")
            rows.append(row)
        return rows


def total_by_category(rows):
    totals = defaultdict(Decimal)
    for row in rows:
        totals[row.get("category") or "khac"] += row["amount"]
    return dict(totals)
