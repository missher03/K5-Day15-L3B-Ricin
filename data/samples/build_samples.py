"""Sinh dữ liệu mẫu cho CodeOwn — phần C (Lê Thành Nguyên). Chỉ dùng thư viện chuẩn, seed 42.

    python data/samples/build_samples.py          ghi lại toàn bộ data/samples/ (repo*/, sessions/, fixtures/, index.json)
    python data/samples/build_samples.py --check  chỉ sinh trong bộ nhớ + kiểm, không ghi file

Mọi thứ ở đây là TỰ DỰNG (synthetic), không phải bằng chứng pain. Mô tả đầy đủ: data/DATA_CARD.md.

Mỗi repo mẫu  data/samples/repoNN_<tên>/
    repo/<file>        file sau commit (để read_file / run_snippet đọc)
    diff.patch         diff của commit "AI viết" (một hunk / file, đủ để git apply)
    events.jsonl       log sự kiện theo hợp đồng task.md mục 0.2
    meta.json          thứ lõi được phép đọc: nhánh, commit message, mô tả task (có thể trống)
    sim_answers.json   câu trả lời giả lập của người dùng, chỉ dùng cho mode "task" (simulate chi phí)
    truth.json         ĐÁP ÁN: nhãn từng dòng, f1..f5, DI, luật nhắc. Lõi / agent KHÔNG được đọc file này.
Mỗi phiên log data/samples/sessions/sessNN/  events.jsonl · diff.patch · meta.json · truth.json

Quy tắc gán nhãn đúng như task.md mục A (attribution) để code của A khớp được 100%:
    dòng thêm trùng hash một dòng trong ai_edit → ai_giu_nguyen
    không trùng nhưng SequenceMatcher ≥ 0,6 với một dòng AI → ai_da_sua
    còn lại → nguoi_viet ;  bỏ dòng trống / chỉ có dấu ngoặc
Script tự kiểm: dòng người viết luôn < 0,6 với mọi dòng AI; dòng AI-đã-sửa luôn ≥ 0,6 với bản AI gốc.
"""
import datetime
import difflib
import hashlib
import json
import os
import random
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 42
TZ = datetime.timezone(datetime.timedelta(hours=7))
START = datetime.datetime(2026, 11, 20, 19, 0, 0, tzinfo=TZ)

SKIP_RE = re.compile(r"^[\s()\[\]{};,]*$")                 # dòng trống / chỉ dấu ngoặc
ERR_RE = re.compile(r"[A-Za-z_.]*(?:Error|Exception)\b[^\n]*")  # dòng lỗi đầu tiên trong prompt
SIM_MOD = 0.6     # ngưỡng ai_da_sua (design.md §5.1)
SIM_ERR = 0.8     # ngưỡng "cùng lỗi" cho f3
F3_CAP, F4_CAP = 5, 600
WEIGHTS = {"f1": 0.30, "f2": 0.25, "f3": 0.20, "f4": 0.15, "f5": 0.10}   # design.md §5.1
DEPENDENT = {"lam_ho", "debug_dan_loi"}
DOC_EXT = {".md", ".txt", ".rst", ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg"}
NUDGE_GAP = 15 * 60


# ================================================================ tiện ích

def sha1(line):
    return hashlib.sha1(line.strip().encode("utf-8")).hexdigest()


def ratio(a, b):
    return difflib.SequenceMatcher(None, a.strip(), b.strip()).ratio()


def skip_line(code):
    return bool(SKIP_RE.match(code))


def is_test(path):
    base = os.path.basename(path)
    return base.startswith("test_") or base.endswith("_test.py") or ".test." in base or "/tests/" in "/" + path


def iso(t):
    return t.isoformat(timespec="seconds")


def err_sig(text):
    m = ERR_RE.search(text or "")
    return m.group(0).strip() if m else None


def n_questions(di):
    return 2 if di < 40 else (3 if di <= 70 else 5)


# ================================================================ repo mẫu viết tay
# Mỗi dòng: "= " không đổi · "- " bị xoá · "A " AI viết, giữ nguyên · "H " người viết
#           "M " AI viết rồi người sửa: "<bản cuối> <<AI>> <bản AI gốc>"

REPOS = [
    {
        "name": "repo01_flask_crud", "lang": "python", "tool": "claude_code",
        "branch": "feat/todo-update-delete", "commit_message": "Thêm PUT và DELETE cho /todos",
        "description": "Thêm API sửa và xoá todo",
        "intent_expected": "Thêm API sửa / xoá todo (khớp nhánh, commit, prompt đầu)",
        "prompts": [
            ("Thêm giúp mình API sửa và xoá todo cho app Flask này, dùng sqlite như phần list.", "lam_ho", True),
            ("sqlite3.OperationalError: no such table: todos", "debug_dan_loi", False),
            ("Sao lại dùng dấu ? trong câu SQL mà không ghép chuỗi f-string cho gọn?", "hoi_khai_niem", False),
            ("ok chạy được rồi, cảm ơn", "khac", False),
        ],
        "edit_after": {"app.py": 0}, "review_gap": 420,
        "files": {"app.py": r'''
= import sqlite3
= from flask import Flask, jsonify, request
=
= app = Flask(__name__)
= DB_PATH = "todo.db"
=
=
= def get_db():
=     conn = sqlite3.connect(DB_PATH)
=     conn.row_factory = sqlite3.Row
=     return conn
=
=
= @app.get("/todos")
= def list_todos():
=     with get_db() as conn:
=         rows = conn.execute("SELECT id, title, done FROM todos").fetchall()
=     return jsonify([dict(r) for r in rows])
A
A
A @app.put("/todos/<int:todo_id>")
A def update_todo(todo_id):
A     data = request.get_json(silent=True) or {}
A     title = (data.get("title") or "").strip()
A     done = bool(data.get("done", False))
A     if not title or len(title) > 200:
A         return jsonify({"error": "title phải có 1-200 ký tự"}), 400
A     with get_db() as conn:
A         cur = conn.execute(
A             "UPDATE todos SET title = ?, done = ? WHERE id = ?",
A             (title, int(done), todo_id),
A         )
A     if cur.rowcount == 0:
M         return jsonify({"error": "không tìm thấy todo"}), 404 <<AI>>         return jsonify({"error": "not found"}), 404
A     return jsonify({"id": todo_id, "title": title, "done": done})
A
A
A @app.delete("/todos/<int:todo_id>")
A def delete_todo(todo_id):
A     with get_db() as conn:
A         deleted = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,)).rowcount
H     # xoá id không tồn tại vẫn trả 404 để client biết gõ sai id
A     if not deleted:
A         return jsonify({"error": "todo không tồn tại"}), 404
A     return "", 204
'''},
        "sim_answers": [
            "Dấu ? là tham số của sqlite3, giá trị truyền riêng nên chuỗi người dùng không thành câu lệnh SQL, tránh SQL injection.",
            "rowcount bằng 0 nghĩa là không có dòng nào bị sửa, tức id không có nên trả 404.",
            "không biết",
        ],
    },
    {
        "name": "repo02_csv_report", "lang": "python", "tool": "claude_code",
        "branch": "feat/csv-total", "commit_message": "Đọc CSV xuất từ Excel, cộng tổng theo category, thêm test",
        "description": "Đọc file CSV Excel và cộng tổng tiền theo nhóm",
        "intent_expected": "Đọc CSV từ Excel và cộng tổng theo nhóm",
        "prompts": [
            ("Sửa hàm load_rows để đọc được file CSV xuất từ Excel, có dấu phẩy hàng nghìn và dòng trống.", "lam_ho", False),
            ("Mình nghĩ lỗi UnicodeDecodeError là do file Excel lưu có BOM ở đầu, đúng không? Có nên mở bằng utf-8-sig?", "debug_co_gia_thuyet", False),
            ("Viết thêm hàm cộng tổng theo category", "lam_ho", False),
            ("Vì sao dùng Decimal mà không dùng float cho tiền?", "hoi_khai_niem", False),
        ],
        "edit_after": {"report.py": 0}, "review_gap": 1500,
        "files": {"report.py": r'''
= import csv
A from collections import defaultdict
A from decimal import Decimal, InvalidOperation
=
=
= def load_rows(path):
-     with open(path) as f:
-         return list(csv.reader(f))
A     with open(path, newline="", encoding="utf-8-sig") as f:
A         reader = csv.DictReader(f)
A         rows = []
A         for i, row in enumerate(reader, start=2):
A             amount = (row.get("amount") or "").strip()
A             if not amount:
A                 continue
A             try:
A                 row["amount"] = Decimal(amount.replace(",", ""))
A             except InvalidOperation:
A                 raise ValueError(f"dòng {i}: amount không hợp lệ: {amount!r}")
A             rows.append(row)
A         return rows
A
A
A def total_by_category(rows):
A     totals = defaultdict(Decimal)
A     for row in rows:
M         totals[row.get("category") or "khac"] += row["amount"] <<AI>>         totals[row.get("category", "other")] += row["amount"]
A     return dict(totals)
''', "tests/test_report.py": r'''
H import report
H
H
H def test_bo_qua_dong_thieu_amount(tmp_path):
H     p = tmp_path / "data.csv"
H     p.write_text("category,amount\nan,1000\nan,\n", encoding="utf-8")
H     assert len(report.load_rows(str(p))) == 1
H
H
H def test_cong_theo_nhom(tmp_path):
H     p = tmp_path / "data.csv"
H     p.write_text('category,amount\nan,"1,000"\nan,500\n', encoding="utf-8")
H     assert report.total_by_category(report.load_rows(str(p))) == {"an": 1500}
'''},
        "sim_answers": [
            "utf-8-sig bỏ ký tự BOM mà Excel ghi ở đầu file, nếu không cột đầu sẽ có tên lạ.",
            "Decimal giữ đúng số thập phân, float cộng tiền bị sai số kiểu 0.1 + 0.2.",
            "Dòng trống thì bỏ qua để khỏi lỗi.",
        ],
    },
    {
        "name": "repo03_auth_login", "lang": "python", "tool": "claude_code",
        "branch": "feat/login", "commit_message": "Đăng nhập có hash mật khẩu và khoá tài khoản",
        "description": "",
        "intent_expected": "Đăng nhập có hash mật khẩu và khoá tài khoản khi sai nhiều lần",
        "prompts": [
            ("Làm giúp mình chức năng đăng nhập có hash mật khẩu và khoá tài khoản khi sai nhiều lần.", "lam_ho", True),
            ("ValueError: not enough values to unpack (expected 2, got 1)", "debug_dan_loi", False),
            ("vẫn lỗi\nValueError: not enough values to unpack (expected 2, got 1)\n  File \"auth.py\", line 21, in verify_password", "debug_dan_loi", False),
            ("ok", "khac", False),
        ],
        "edit_after": {"auth.py": 0}, "review_gap": 40,
        "files": {"auth.py": r'''
A import hashlib
A import hmac
A import os
A import time
A
A ITERATIONS = 200_000
A MAX_ATTEMPTS = 5
A LOCK_SECONDS = 300
A _failed = {}
A
A
A def hash_password(password: str) -> str:
A     salt = os.urandom(16)
A     digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
A     return salt.hex() + "$" + digest.hex()
A
A
A def verify_password(password: str, stored: str) -> bool:
A     salt_hex, digest_hex = stored.split("$", 1)
A     digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), ITERATIONS)
A     return hmac.compare_digest(digest.hex(), digest_hex)
A
A
A def login(username: str, password: str, users: dict) -> bool:
A     count, since = _failed.get(username, (0, 0.0))
A     if count >= MAX_ATTEMPTS and time.monotonic() - since < LOCK_SECONDS:
A         raise PermissionError("tài khoản tạm khoá, thử lại sau")
A     stored = users.get(username)
A     if stored is None or not verify_password(password, stored):
A         _failed[username] = (count + 1, time.monotonic())
A         return False
A     _failed.pop(username, None)
A     return True
'''},
        "sim_answers": [
            "compare_digest so sánh hết chuỗi trong thời gian như nhau nên không đo được thời gian để đoán hash.",
            "Salt ngẫu nhiên để hai người cùng mật khẩu có hash khác nhau.",
            "Hash mật khẩu cho an toàn.",
        ],
    },
    {
        "name": "repo04_js_weather", "lang": "javascript", "tool": "cursor",
        "branch": "feat/weather-timeout", "commit_message": "getWeather có timeout và retry",
        "description": "Gọi API thời tiết không bị treo khi mạng chậm",
        "intent_expected": "Gọi API thời tiết có timeout và retry khi lỗi mạng",
        "prompts": [
            ("Viết lại getWeather có timeout 5 giây và retry khi lỗi mạng", "lam_ho", False),
            ("AbortController hoạt động thế nào, abort xong thì fetch ném lỗi gì?", "hoi_khai_niem", False),
            ("Mình đoán retry khi gặp 4xx là sai vì lỗi do phía client, nên chỉ retry 5xx và lỗi mạng đúng không?", "debug_co_gia_thuyet", False),
        ],
        "edit_after": {"weather.js": 0}, "review_gap": 600,
        "files": {"weather.js": r'''
= const API = "https://api.example-weather.test/v1/current";
=
- export async function getWeather(city) {
-   const res = await fetch(`${API}?city=${city}`);
-   return res.json();
- }
A export async function getWeather(city, { retries = 2, timeoutMs = 5000 } = {}) {
A   const url = `${API}?city=${encodeURIComponent(city)}`;
A   for (let attempt = 0; attempt <= retries; attempt++) {
A     const controller = new AbortController();
A     const timer = setTimeout(() => controller.abort(), timeoutMs);
A     try {
A       const res = await fetch(url, { signal: controller.signal });
A       if (res.status >= 500) throw new Error(`server ${res.status}`);
H       // 4xx là lỗi phía mình (sai tên city), thử lại cũng vô ích nên trả luôn
A       if (!res.ok) return { error: `HTTP ${res.status}` };
A       return await res.json();
A     } catch (err) {
A       if (attempt === retries) return { error: err.name === "AbortError" ? "timeout" : err.message };
M       await new Promise((r) => setTimeout(r, 500 * 2 ** attempt)); <<AI>>       await new Promise((r) => setTimeout(r, 300 * 2 ** attempt));
A     } finally {
A       clearTimeout(timer);
A     }
A   }
A }
'''},
        "sim_answers": [
            "Hết timeoutMs thì controller.abort() làm fetch ném AbortError, catch bắt và thử lại hoặc trả timeout.",
            "Chờ 500ms rồi gấp đôi mỗi lần để server đỡ bị dồn request.",
            "finally để dọn timer.",
        ],
    },
    {
        "name": "repo05_upload", "lang": "python", "tool": "claude_code",
        "branch": "feat/upload", "commit_message": "Upload ảnh / pdf giới hạn 5MB",
        "description": "Cho người dùng tải ảnh hoặc pdf lên",
        "intent_expected": "Upload ảnh / pdf có giới hạn dung lượng",
        "prompts": [
            ("Làm chức năng upload ảnh và pdf cho mình, giới hạn 5MB.", "lam_ho", True),
            ("Sao phải đổi tên file thành uuid, giữ tên gốc không được à?", "hoi_khai_niem", False),
            ("commit giúp mình", "khac", False),
        ],
        "edit_after": {"upload.py": 0}, "review_gap": 180,
        "files": {"upload.py": r'''
A import os
A import uuid
A
A UPLOAD_DIR = os.path.abspath("uploads")
A ALLOWED = {".png", ".jpg", ".jpeg", ".pdf"}
A MAX_BYTES = 5 * 1024 * 1024
A
A
A def save_upload(filename: str, data: bytes) -> str:
A     ext = os.path.splitext(filename)[1].lower()
A     if ext not in ALLOWED:
A         raise ValueError("định dạng không cho phép")
A     if len(data) > MAX_BYTES:
M         raise ValueError("file vượt quá 5MB") <<AI>>         raise ValueError("file quá lớn")
A     safe_name = uuid.uuid4().hex + ext
A     path = os.path.join(UPLOAD_DIR, safe_name)
A     if not os.path.abspath(path).startswith(UPLOAD_DIR + os.sep):
A         raise ValueError("đường dẫn không hợp lệ")
A     os.makedirs(UPLOAD_DIR, exist_ok=True)
A     with open(path, "wb") as f:
A         f.write(data)
A     return safe_name
'''},
        "sim_answers": [
            "Tên gốc có thể chứa ../ để ghi ra ngoài thư mục uploads, đổi sang uuid thì không đoán và không vượt thư mục được.",
            "Kiểm đuôi file để chỉ nhận ảnh và pdf.",
            "không rõ lắm",
        ],
    },
    {
        "name": "repo06_sql_search", "lang": "python", "tool": "claude_code",
        "branch": "fix/search-injection", "commit_message": "Search dùng tham số, thêm phân trang",
        "description": "Sửa lỗi SQL injection ở tìm kiếm sản phẩm",
        "intent_expected": "Chặn SQL injection ở tìm kiếm + phân trang",
        "prompts": [
            ("Mình nghĩ search bị SQL injection vì ghép keyword thẳng vào f-string, sửa sang tham số được không?", "debug_co_gia_thuyet", False),
            ("Thêm phân trang cho search_products", "lam_ho", False),
            ("ESCAPE trong LIKE để làm gì?", "hoi_khai_niem", False),
        ],
        "edit_after": {"search.py": 1}, "review_gap": 900,
        "files": {"search.py": r'''
= import sqlite3
=
=
- def search_products(conn, keyword):
-     sql = f"SELECT id, name, price FROM products WHERE name LIKE '%{keyword}%'"
-     return conn.execute(sql).fetchall()
A def _escape_like(text: str) -> str:
A     return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
A
A
A def search_products(conn: sqlite3.Connection, keyword: str, page: int = 1, per_page: int = 20):
A     page = max(page, 1)
H     per_page = min(max(per_page, 1), 100)  # chặn client xin cả triệu dòng một lần
A     pattern = "%" + _escape_like(keyword.strip()) + "%"
A     sql = (
A         "SELECT id, name, price FROM products "
A         "WHERE name LIKE ? ESCAPE '\\' "
A         "ORDER BY name LIMIT ? OFFSET ?"
A     )
A     return conn.execute(sql, (pattern, per_page, (page - 1) * per_page)).fetchall()
'''},
        "sim_answers": [
            "keyword đi qua tham số ? nên không thành câu lệnh SQL; _escape_like để % và _ người dùng gõ được hiểu là ký tự thường.",
            "OFFSET = (page - 1) * per_page để bỏ qua các trang trước.",
            "Để search nhanh hơn.",
        ],
    },
    {
        "name": "repo07_format_only", "lang": "python", "tool": "claude_code",
        "branch": "chore/format", "commit_message": "Format utils.py theo PEP8",
        "description": "Format lại code",
        "intent_expected": "Chỉ format + đổi tên biến, không đổi logic",
        "skip_reason": "dinh_dang",
        "prompts": [
            ("Format lại file utils.py theo PEP8 và đổi tên biến s cho dễ đọc", "khac", False),
        ],
        "edit_after": {"utils.py": 0}, "review_gap": 60,
        "files": {"utils.py": r'''
= import re
=
=
- def slugify(s):
-     s=s.lower().strip()
-     s=re.sub(r'[^a-z0-9]+','-',s)
-     return s.strip('-')
A def slugify(text):
A     text = text.lower().strip()
A     text = re.sub(r"[^a-z0-9]+", "-", text)
A     return text.strip("-")
'''},
        "sim_answers": ["Chỉ đổi format.", "không biết", "Đổi tên biến."],
    },
    {
        "name": "repo08_js_debounce", "lang": "javascript", "tool": "cursor",
        "branch": "feat/search-debounce", "commit_message": "Debounce ô tìm kiếm",
        "description": "Ô tìm kiếm gọi API quá nhiều",
        "intent_expected": "Debounce ô tìm kiếm, bỏ kết quả cũ",
        "prompts": [
            ("Ô tìm kiếm gọi API mỗi lần gõ phím, làm debounce giúp", "lam_ho", False),
            ("TypeError: render is not a function", "debug_dan_loi", False),
            ("TypeError: render is not a function\n    at onSearchInput (search-box.js:13)", "debug_dan_loi", False),
            ("vẫn bị\nTypeError: render is not a function", "debug_dan_loi", False),
        ],
        "edit_after": {"search-box.js": 0}, "review_gap": 25,
        "files": {"search-box.js": r'''
A export function debounce(fn, waitMs = 300) {
A   let timer = null;
A   return (...args) => {
A     clearTimeout(timer);
A     timer = setTimeout(() => fn(...args), waitMs);
A   };
A }
A
A let latestRequest = 0;
A
A export async function onSearchInput(query, render) {
A   const requestId = ++latestRequest;
A   if (query.trim().length < 2) return render([]);
A   const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
A   const items = await res.json();
A   if (requestId !== latestRequest) return;
A   render(items);
A }
A
A export const searchHandler = debounce(onSearchInput, 300);
'''},
        "sim_answers": [
            "Mỗi lần gõ thì clearTimeout hẹn giờ cũ, chỉ gọi khi ngừng gõ 300ms.",
            "requestId để bỏ kết quả của request cũ về muộn.",
            "không biết",
        ],
    },
    {
        "name": "repo09_py_cache", "lang": "python", "tool": "claude_code",
        "branch": "main", "commit_message": "update",
        "description": "",
        "intent_expected": "chưa rõ (nhánh main, commit 'update', prompt mơ hồ)",
        "prompts": [
            ("làm tiếp cái hôm qua", "khac", False),
            ("thêm cache", "lam_ho", False),
            ("ok", "khac", False),
        ],
        "edit_after": {"cache.py": 1}, "review_gap": 90,
        "files": {"cache.py": r'''
A import threading
A import time
A
A
A class TTLCache:
A     def __init__(self, ttl_seconds: float = 60.0, max_items: int = 1000):
A         self.ttl = ttl_seconds
A         self.max_items = max_items
A         self._data = {}
A         self._lock = threading.Lock()
A
A     def get(self, key):
A         with self._lock:
A             item = self._data.get(key)
A             if item is None:
A                 return None
A             value, expires_at = item
A             if time.monotonic() >= expires_at:
A                 del self._data[key]
A                 return None
A             return value
A
A     def set(self, key, value):
A         with self._lock:
A             if len(self._data) >= self.max_items:
A                 oldest = min(self._data, key=lambda k: self._data[k][1])
A                 del self._data[oldest]
A             self._data[key] = (value, time.monotonic() + self.ttl)
'''},
        "sim_answers": [
            "monotonic không bị nhảy khi đổi giờ hệ thống nên hạn TTL không sai.",
            "Lock để hai luồng không cùng sửa _data.",
            "Cache cho nhanh.",
        ],
    },
    {
        "name": "repo10_payment_mismatch", "lang": "python", "tool": "claude_code",
        "branch": "fix/login", "commit_message": "Sửa lỗi login không vào được",
        "description": "",
        "intent_expected": "LỆCH: nhánh + commit nói sửa login, nhưng prompt và diff đổi thanh toán (làm tròn tiền, idempotency)",
        "prompts": [
            ("Khách bị trừ tiền 2 lần khi bấm thanh toán nhanh, sửa giúp mình hàm charge", "lam_ho", False),
            ("idempotency key là gì?", "hoi_khai_niem", False),
        ],
        "edit_after": {"payment.py": 0}, "review_gap": 300,
        "files": {"payment.py": r'''
= from decimal import Decimal, ROUND_HALF_UP
=
=
= def charge(order, gateway):
-     amount = round(order["total"] * 1.1, 2)
-     return gateway.charge(order["id"], amount)
A     amount = (Decimal(str(order["total"])) * Decimal("1.1")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
A     idem_key = f"order-{order['id']}"
A     if gateway.already_charged(idem_key):
A         return {"status": "duplicate", "idempotency_key": idem_key}
A     return gateway.charge(order["id"], amount, idempotency_key=idem_key)
'''},
        "sim_answers": [
            "Cùng một order thì cùng idem_key, cổng thanh toán thấy key đã dùng thì không trừ tiền lần hai.",
            "quantize làm tròn 2 chữ số theo kiểu nửa lên.",
            "không biết",
        ],
    },
    {
        "name": "repo11_js_jwt", "lang": "javascript", "tool": "claude_code",
        "branch": "feat/auth-middleware", "commit_message": "Middleware kiểm JWT",
        "description": "Bảo vệ các route cần đăng nhập",
        "intent_expected": "Middleware kiểm JWT cho Express",
        "prompts": [
            ("Viết middleware kiểm JWT cho express", "lam_ho", True),
            ("Vì sao phải truyền algorithms vào jwt.verify?", "hoi_khai_niem", False),
            ("Mình nghĩ bị 401 hoài là do header gửi thiếu chữ Bearer, đúng không?", "debug_co_gia_thuyet", False),
        ],
        "edit_after": {"auth-middleware.js": 0}, "review_gap": 360,
        "files": {"auth-middleware.js": r'''
A const jwt = require("jsonwebtoken");
A
A function requireAuth(req, res, next) {
A   const header = req.headers.authorization || "";
A   const [scheme, token] = header.split(" ");
A   if (scheme !== "Bearer" || !token) {
A     return res.status(401).json({ error: "thiếu token" });
A   }
A   try {
H     // chỉ nhận HS256 để chặn token giả mạo kiểu alg none
A     req.user = jwt.verify(token, process.env.JWT_SECRET, { algorithms: ["HS256"] });
A     return next();
A   } catch (err) {
M     const msg = err.name === "TokenExpiredError" ? "token đã hết hạn" : "token không hợp lệ"; <<AI>>     const msg = err.name === "TokenExpiredError" ? "token expired" : "invalid token";
A     return res.status(401).json({ error: msg });
A   }
A }
A
A module.exports = { requireAuth };
'''},
        "sim_answers": [
            "Không chỉ định algorithms thì token giả có thể khai alg khác; khoá HS256 để chỉ nhận đúng kiểu ký mình dùng.",
            "Header phải dạng 'Bearer <token>', thiếu thì trả 401.",
            "không biết",
        ],
    },
    {
        "name": "repo12_docs_only", "lang": "markdown", "tool": "claude_code",
        "branch": "docs/readme", "commit_message": "Cập nhật README và cổng chạy",
        "description": "Viết hướng dẫn chạy",
        "intent_expected": "Chỉ đổi docs + config",
        "skip_reason": "docs_config",
        "prompts": [("Viết lại phần hướng dẫn chạy trong README, đổi cổng sang 8080", "lam_ho", False)],
        "edit_after": {"README.md": 0, "config.yaml": 0}, "review_gap": 120,
        "files": {"README.md": r'''
= # Todo API
=
- Chạy: python app.py
A ## Cách chạy
A
A 1. Cài Flask: `pip install flask`
A 2. Chạy: `python app.py`
A 3. Mở http://localhost:8080/todos
''', "config.yaml": r'''
- port: 5000
A port: 8080
A debug: false
'''},
        "sim_answers": ["Đổi cổng.", "không biết", "Viết docs."],
    },
]


def parse_annotated(text):
    """→ (dòng trước commit, [(code, tag, bản AI gốc)] sau commit, [(tag, code)] theo thứ tự diff)."""
    before, after, order = [], [], []
    for raw in text.strip("\n").split("\n"):
        tag, body = raw[:1], raw[2:]
        if tag == "=":
            before.append(body)
            after.append((body, "=", None))
            order.append((" ", body))
        elif tag == "-":
            before.append(body)
            order.append(("-", body))
        elif tag == "A":
            after.append((body, "A", body))
            order.append(("+", body))
        elif tag == "H":
            after.append((body, "H", None))
            order.append(("+", body))
        elif tag == "M":
            left, right = body.split("<<AI>>")
            final, orig = left[:-1], right[1:]
            after.append((final, "M", orig))
            order.append(("+", final))
        else:
            raise ValueError("dòng không có nhãn hợp lệ: %r" % raw)
    return before, after, order


def unified_diff(path, before, after, order):
    """Một hunk phủ cả file — đúng định dạng unified diff, git apply được."""
    new = not before
    out = ["diff --git a/%s b/%s" % (path, path)]
    if new:
        out.append("new file mode 100644")
    out.append("--- " + ("/dev/null" if new else "a/" + path))
    out.append("+++ b/" + path)
    out.append("@@ -%s +1,%d @@" % ("0,0" if new else "1,%d" % len(before), len(after)))
    out += [sign + code for sign, code in order]
    return "\n".join(out) + "\n"


# ================================================================ chấm "sự thật" từ cách dựng

def label_lines(files):
    """files: {path: [(code, tag, orig)]} → (lines, ai_lines_by_file, problems)."""
    tag_label = {"A": "ai_giu_nguyen", "M": "ai_da_sua", "H": "nguoi_viet"}
    ai_by_file = {}
    for path, rows in files.items():
        ai_by_file[path] = [orig for code, tag, orig in rows if tag in ("A", "M") and not skip_line(orig)]
    ai_all = [l for ls in ai_by_file.values() for l in ls]
    ai_hash = {sha1(l) for l in ai_all}
    lines, problems = [], []
    for path, rows in files.items():
        for k, (code, tag, orig) in enumerate(rows, start=1):
            if tag == "=" or skip_line(code):
                continue
            if tag == "H":
                best = max((ratio(code, a) for a in ai_all), default=0.0)
                if sha1(code) in ai_hash or best >= SIM_MOD:
                    problems.append("%s:%d người viết nhưng giống dòng AI %.2f: %s" % (path, k, best, code.strip()))
            if tag == "M":
                r = ratio(code, orig)
                if sha1(code) in ai_hash or r < SIM_MOD:
                    problems.append("%s:%d AI-đã-sửa nhưng ratio %.2f: %s" % (path, k, r, code.strip()))
            lines.append({"file": path, "line": k, "code": code, "label": tag_label[tag]})
    return lines, ai_by_file, problems


def features(lines, events, commit_ts):
    stats = {"ai_giu_nguyen": 0, "ai_da_sua": 0, "nguoi_viet": 0}
    for l in lines:
        stats[l["label"]] += 1
    ai_n = stats["ai_giu_nguyen"] + stats["ai_da_sua"]
    f1 = stats["ai_giu_nguyen"] / ai_n if ai_n else 0.0
    prompts = [e for e in events if e["event"] == "prompt"]
    labels = [e["_label"] for e in prompts]
    f2 = sum(1 for x in labels if x in DEPENDENT) / len(labels) if labels else 0.0
    # f3: số chuỗi ≥2 prompt liền nhau có cùng dòng lỗi (≥0,8). Log tự dựng không có sự kiện người sửa giữa hai prompt.
    sigs = [err_sig(e["prompt"]) for e in prompts]
    f3, run, max_run, run_end = 0, 1, 1, None
    for i in range(1, len(sigs) + 1):
        same = i < len(sigs) and sigs[i] and sigs[i - 1] and ratio(sigs[i], sigs[i - 1]) >= SIM_ERR
        if same:
            run += 1
            if run >= 3 and run_end is None:
                run_end = prompts[i]
        else:
            if run >= 2:
                f3 += 1
            max_run = max(max_run, run)
            run = 1
    # f4: trung vị giây từ ai_edit chứa dòng tới commit (dòng AI có trong commit)
    edit_ts = {}
    for e in events:
        if e["event"] == "ai_edit":
            for h in e["line_hashes"]:
                edit_ts.setdefault(h, e["_t"])
    waits = []
    for l in lines:
        if l["label"] == "nguoi_viet":
            continue
        h = sha1(l["code"]) if l["label"] == "ai_giu_nguyen" else l["_orig_hash"]
        if h in edit_ts:
            waits.append((commit_ts - edit_ts[h]).total_seconds())
    f4 = statistics.median(waits) if waits else float(F4_CAP)
    f5 = 1 if any(l["label"] == "nguoi_viet" and is_test(l["file"]) for l in lines) else 0
    f3n = min(f3, F3_CAP) / F3_CAP
    f4n = min(f4, F4_CAP) / F4_CAP
    di_exact = 100 * (WEIGHTS["f1"] * f1 + WEIGHTS["f2"] * f2 + WEIGHTS["f3"] * f3n
                      + WEIGHTS["f4"] * (1 - f4n) + WEIGHTS["f5"] * (1 - f5))
    feats = {"f1": round(f1, 4), "f2": round(f2, 4), "f3": f3, "f4_sec": round(f4, 1), "f5": f5}
    return stats, feats, {"f3n": round(f3n, 4), "f4n": round(f4n, 4)}, di_exact, max_run, run_end


def nudges(events, max_run, run_end, di, commit_event):
    """Luật nhắc ở task.md mục A / design.md §5.3. → (luật kích hoạt, danh sách nhắc thật sự bật sau giới hạn 15 phút)."""
    trig = []
    if max_run >= 3 and run_end is not None:
        trig.append(("lap_loi", run_end))
    edits = [e for e in events if e["event"] == "ai_edit"]
    for i, e in enumerate(edits):
        window = [x for x in edits if 0 <= (x["_t"] - e["_t"]).total_seconds() < 30]
        if sum(len(x["line_hashes"]) for x in window) >= 50:
            trig.append(("nhan_nhieu_dong", window[-1]))
            break
    for e in events:
        if e["event"] == "prompt" and e.get("_feature"):
            trig.append(("lam_ho_ca_tinh_nang", e))
            break
    if di > 70:
        trig.append(("di_cao", commit_event))
    trig.sort(key=lambda x: x[1]["_t"])
    fired, last = [], None
    for rule, e in trig:
        if last is None or (e["_t"] - last).total_seconds() >= NUDGE_GAP:
            fired.append({"rule": rule, "ts": iso(e["_t"]), "event_id": e["id"]})
            last = e["_t"]
    return sorted({r for r, _ in trig}), fired


# ================================================================ dựng log sự kiện

class Clock:
    def __init__(self, start):
        self.t = start

    def add(self, sec):
        self.t = self.t + datetime.timedelta(seconds=sec)
        return self.t


def build_events(rng, prefix, task_id, session_id, tool, branch, prompts, edits, review_gap, commit_message, model):
    """prompts: [(text, label, feature)] · edits: [(prompt_idx, path, [dòng AI])] → danh sách sự kiện (còn khoá _ riêng)."""
    clock = Clock(START + datetime.timedelta(days=rng.randint(0, 6), minutes=rng.randint(0, 120)))
    ev, k = [], [0]

    def add(event, **kw):
        k[0] += 1
        e = {"id": "ev_%s%04d" % (prefix, k[0]), "ts": iso(clock.t), "task_id": task_id, "tool": tool,
             "event": event, "session_id": session_id, "model": model if event != "commit" else None,
             "branch": branch, "commit": None, "prompt": None, "file": None, "line_hashes": [], "meta": {}}
        e.update(kw)
        e["_t"] = clock.t
        ev.append(e)
        return e

    for i, (text, label, feature) in enumerate(prompts):
        if i:
            clock.add(rng.randint(30, 240))
        e = add("prompt", prompt=text[:1000])
        e["_label"], e["_feature"] = label, feature
        mine = [x for x in edits if x[0] == i]
        for _, path, ai_lines in mine:
            clock.add(rng.randint(4, 25))
            add("ai_edit", file=path, line_hashes=[sha1(l) for l in ai_lines],
                meta={"tool_name": rng.choice(["Write", "Edit", "MultiEdit"]), "n_lines": len(ai_lines)})
        if label.startswith("debug") or rng.random() < 0.4:
            clock.add(rng.randint(3, 15))
            add("ai_bash", meta={"command": rng.choice(["python -m pytest -q", "python app.py", "npm test", "node index.js"])})
        clock.add(rng.randint(2, 8))
        add("ai_turn_end")
    clock.add(review_gap)
    c = add("commit", tool="git", commit="%040x" % rng.getrandbits(160), meta={"message": commit_message})
    return ev, c


def public(events):
    return [{k: v for k, v in e.items() if not k.startswith("_")} for e in events]


def finish(rng, prefix, ident, files, prompts, edits, branch, commit_message, review_gap, tool, model, extra_truth):
    lines, ai_by_file, problems = label_lines(files)
    orig_hash = {}
    for path, rows in files.items():
        for k, (code, tag, orig) in enumerate(rows, start=1):
            if tag == "M":
                orig_hash[(path, k)] = sha1(orig)
    for l in lines:
        l["_orig_hash"] = orig_hash.get((l["file"], l["line"]))
    # edits: (prompt_idx, path) = mọi dòng AI của file · (prompt_idx, path, đầu, cuối) = một đoạn
    edits = [(e[0], e[1], ai_by_file[e[1]][e[2]:e[3]] if len(e) > 2 else ai_by_file[e[1]])
             for e in edits if ai_by_file.get(e[1])]
    edits = [e for e in edits if e[2]]
    events, commit = build_events(rng, prefix, ident["task_id"], ident["session_id"], tool, branch, prompts, edits,
                                  review_gap, commit_message, model)
    stats, feats, norm, di_exact, max_run, run_end = features(lines, events, commit["_t"])
    di = int(di_exact + 0.5)
    rules, fired = nudges(events, max_run, run_end, di, commit)
    total = sum(stats.values())
    ai_n = stats["ai_giu_nguyen"] + stats["ai_da_sua"]
    truth = {
        "task_id": ident["task_id"], "session_id": ident["session_id"], "diff_id": ident.get("diff_id"),
        "lines": [{k: v for k, v in l.items() if not k.startswith("_")} for l in lines],
        "stats": stats, "features": feats, "features_norm": norm,
        "di": di, "di_exact": round(di_exact, 2),
        "prompt_labels": [{"event_id": e["id"], "label": e["_label"], "ca_tinh_nang": bool(e["_feature"])}
                          for e in events if e["event"] == "prompt"],
        "nudge_rules": rules, "nudges_fired": fired,
        "open_check_by_size": ai_n >= 20 or (total and ai_n / total >= 0.3),
        "n_questions_expected": n_questions(di),
    }
    truth.update(extra_truth)
    return truth, public(events), problems


# ================================================================ phiên log sinh tự động

NAMES = ["user", "order", "item", "price", "total", "row", "record", "token", "config", "result", "payload",
         "cart", "invoice", "path", "email", "count", "limit", "page", "report", "product"]
ATTRS = ["id", "price", "qty", "status", "created_at", "amount", "name", "email"]
FUNCS = ["load", "parse", "validate", "fetch", "save", "compute", "send", "read", "normalize", "build"]
EXC = ["KeyError", "ValueError", "TimeoutError", "OSError", "TypeError", "AttributeError"]
MODULES = ["orders", "users", "cart", "billing", "reports", "inventory", "auth", "mailer"]
FEATS = ["giỏ hàng", "đăng ký tài khoản", "xuất báo cáo PDF", "tìm kiếm sản phẩm", "đặt lịch hẹn", "quên mật khẩu"]
CONCEPTS = [("Decimal", "float"), ("dict.get", "dict[key]"), ("with open", "tự gọi close"), ("tham số ? của sqlite3", "f-string"),
            ("async/await", "callback"), ("set", "list"), ("logging", "print"), ("pathlib", "os.path")]

STYLES = {
    #             số prompt   tỉ lệ nhãn: lam_ho, hoi, debug_gt, dan_loi, khac      dòng AI   giữ    người   test  chờ commit (giây)  lặp lỗi
    "tu_luc":    dict(np=(3, 6), w=(0.15, 0.35, 0.30, 0.10, 0.10), ai=(8, 20), keep=0.40, hum=(10, 22), test=0.8, gap=(400, 1500), rep=0.0),
    "can_bang":  dict(np=(3, 7), w=(0.30, 0.25, 0.20, 0.15, 0.10), ai=(20, 40), keep=0.65, hum=(4, 12), test=0.5, gap=(150, 600), rep=0.25),
    "phu_thuoc": dict(np=(4, 8), w=(0.50, 0.05, 0.05, 0.35, 0.05), ai=(35, 70), keep=0.92, hum=(0, 3), test=0.1, gap=(15, 120), rep=0.6),
}
LABELS = ["lam_ho", "hoi_khai_niem", "debug_co_gia_thuyet", "debug_dan_loi", "khac"]


def fill(rng):
    a, b, c = rng.sample(NAMES, 3)
    return {"a": a, "b": b, "c": c, "f": rng.choice(FUNCS), "d": rng.choice(ATTRS), "n": rng.randint(2, 500),
            "e": rng.choice(EXC), "m": rng.choice(MODULES)}


def ai_code(rng):
    v = fill(rng)
    t = [
        "    {a} = {f}_{b}({c})", "    if {a} is None:", "        raise ValueError(\"{a} không hợp lệ\")",
        "    for {a} in {b}_list:", "        {c} += {a}.{d}", "    return {a}_{b}",
        "    {a}_ids = [x.{d} for x in {b}_list if x.{d} > {n}]", "    logger.info(\"{f} {a} xong: %s\", {b})",
        "def {f}_{a}({b}, {c}={n}):", "    try:", "    except {e} as exc:",
        "        return {{\"error\": str(exc), \"{a}\": {b}}}", "    {a}_map = {{x.{d}: x for x in {b}_list}}",
    ]
    return rng.choice(t).format(**v)


def human_code(rng, in_test):
    v = fill(rng)
    if in_test:
        t = ["def test_{f}_{a}_khi_{b}_rong():", "    assert {f}_{a}([]) == []", "    with pytest.raises({e}):",
             "def test_{f}_{a}_dung_so_lieu_mau_{n}():", "    du_lieu_mau = taoDuLieu(so_dong={n})"]
    else:
        t = ["    # TODO hỏi lại anh lead về {a} ở ticket #{n}", "    {a}Cache.clear()  # mình thêm để khỏi đọc dữ liệu cũ",
             "    print('debug tạm', {a}, {b})", "    # {f} chạy chậm khi {b} > {n} phần tử, xem lại sau",
             "    MAX_{a}_RETRY = {n}  # số mình tự chọn sau khi thử tay"]
    return rng.choice(t).format(**v)


def mutate(rng, line):
    words = re.findall(r"[A-Za-z_]+", line)
    cands = [w for w in words if w in NAMES or w in ATTRS]
    if cands:
        w = rng.choice(cands)
        return line.replace(w, rng.choice([x for x in NAMES + ATTRS if x != w]), 1)
    nums = re.findall(r"\d+", line)
    if nums:
        return line.replace(nums[0], str(int(nums[0]) + rng.randint(1, 9)), 1)
    return line.rstrip() + "  # sửa"


PROMPT_T = {
    "lam_ho": ["Viết giúp mình hàm {f}_{a} trong {m}.py", "Sửa {m}.py cho chạy được luôn giúp mình",
               "Thêm xử lý {a} vào {m}.py, viết đầy đủ nha"],
    "lam_ho_feature": ["Làm toàn bộ tính năng {feat} giúp mình, gồm cả API và lưu DB", "Code hết chức năng {feat} luôn nha"],
    "hoi_khai_niem": ["Vì sao nên dùng {c1} thay vì {c2}?", "{c1} khác {c2} ở chỗ nào?", "Khi nào thì cần {c1}?"],
    "debug_co_gia_thuyet": ["Mình nghĩ {f}_{a} trả sai là do {a} bị None khi danh sách rỗng, đúng không?",
                            "Mình đoán {b} chưa được khởi tạo trước vòng lặp nên {f}_{a} hỏng, kiểm giúp giả thuyết này"],
    "debug_dan_loi": ["Traceback (most recent call last):\n  File \"app/{m}.py\", line {n}, in {f}_{a}\n{e}: '{a}'",
                      "{e}: '{b}'", "lỗi nè\n{e}: {f}_{a}() missing 1 required positional argument: '{c}'"],
    "khac": ["ok cảm ơn", "chạy test giúp mình", "tiếp tục đi", "commit giúp mình"],
}


def make_prompt(rng, label, feature=False):
    v = fill(rng)
    c1, c2 = rng.choice(CONCEPTS)
    v.update(c1=c1, c2=c2, feat=rng.choice(FEATS))
    key = "lam_ho_feature" if feature else label
    return rng.choice(PROMPT_T[key]).format(**v)


def make_session(rng, idx, style, force=None):
    force = force or {}
    st = STYLES[style]
    mod = rng.choice(MODULES)
    app_path, test_path = "app/%s.py" % mod, "tests/test_%s.py" % mod
    # prompt
    n_p = rng.randint(*st["np"])
    labels = [rng.choices(LABELS, weights=st["w"])[0] for _ in range(n_p)]
    prompts, i = [], 0
    while i < len(labels):
        lab = labels[i]
        feature = lab == "lam_ho" and i == 0 and style == "phu_thuoc" and rng.random() < 0.6
        text = make_prompt(rng, lab, feature)
        prompts.append((text, lab, feature))
        if lab == "debug_dan_loi" and rng.random() < st["rep"]:
            for _ in range(rng.randint(1, 3)):
                prompts.append((rng.choice(["vẫn lỗi\n", "", "sửa rồi mà vẫn vậy\n"]) + text, "debug_dan_loi", False))
        i += 1
    if force.get("repeat"):
        base = make_prompt(rng, "debug_dan_loi")
        prompts.insert(1, (base, "debug_dan_loi", False))
        prompts.insert(2, ("vẫn lỗi\n" + base, "debug_dan_loi", False))
        prompts.insert(3, ("sửa rồi mà vẫn vậy\n" + base, "debug_dan_loi", False))
    # dòng code
    n_ai = force.get("ai_lines") or rng.randint(*st["ai"])
    ai_lines = []
    while len(ai_lines) < n_ai:
        ai_lines.append(ai_code(rng))
    rows_app = []
    ai_hashes = {sha1(x) for x in ai_lines}
    for line in ai_lines:
        if rng.random() < st["keep"]:
            rows_app.append((line, "A", line))
        else:
            for _ in range(30):
                m = mutate(rng, line)
                if sha1(m) not in ai_hashes and ratio(m, line) >= SIM_MOD and m.strip() != line.strip():
                    rows_app.append((m, "M", line))
                    break
            else:
                rows_app.append((line, "A", line))
    for j in sorted(rng.sample(range(len(rows_app) + 1), k=min(2, len(rows_app)))):
        rows_app.insert(j, (rng.choice(["", "    )", "]"]), "A", ""))   # dòng trống / chỉ ngoặc: phải bị bỏ khi gán nhãn

    def human_ok(code):
        return sha1(code) not in ai_hashes and max((ratio(code, a) for a in ai_lines), default=0) < SIM_MOD

    n_h = rng.randint(*st["hum"])
    test_rows = []
    for _ in range(n_h):
        in_test = rng.random() < st["test"] * 0.5
        for _ in range(40):
            h = human_code(rng, in_test)
            if human_ok(h):
                break
        else:
            continue
        if in_test:
            test_rows.append((h, "H", None))
        else:
            rows_app.insert(rng.randint(0, len(rows_app)), (h, "H", None))
    files = {app_path: rows_app}
    if test_rows:
        files[test_path] = test_rows
    # AI trả code ở các prompt yêu cầu code / gỡ lỗi; phiên "bulk" nhận hết trong một lần (luật ≥50 dòng / 30 giây)
    code_turns = [k for k, (_, lab, _) in enumerate(prompts) if lab in ("lam_ho", "debug_dan_loi", "debug_co_gia_thuyet")] or [0]
    if force.get("bulk"):
        code_turns = code_turns[:1]
    size = -(-n_ai // len(code_turns))
    ai_edits = [(idx, app_path, k * size, (k + 1) * size) for k, idx in enumerate(code_turns)]
    name = "sess%02d" % idx
    ident = {"task_id": name + "_t1", "session_id": name, "diff_id": name + "_c1"}
    review = force.get("review_gap") or rng.randint(*st["gap"])
    truth, events, problems = finish(rng, "9%02d" % idx, ident, files, prompts, ai_edits,
                                     "feat/%s-%s" % (mod, name), "Cập nhật %s" % mod, review,
                                     "claude_code", "claude-sonnet-5-5", {"style": style})
    diff = "".join(unified_diff(p, [], [c for c, _, _ in rows], [("+", c) for c, _, _ in rows]) for p, rows in files.items())
    meta = {"session_id": name, "task_id": ident["task_id"], "diff_id": ident["diff_id"], "branch": "feat/%s-%s" % (mod, name),
            "commit_message": "Cập nhật %s" % mod, "description": "", "files": list(files)}
    return name, {"events": events, "diff": diff, "meta": meta, "truth": truth}, problems


# ================================================================ fixtures cho A và B

CLASSIFIER_PROMPTS = [
    ("Viết giúp mình API đăng ký tài khoản bằng Flask, có kiểm email trùng", "lam_ho"),
    ("Làm hết phần giỏ hàng luôn, mình cần nộp tối nay", "lam_ho"),
    ("Sửa file này cho chạy được giúp mình", "lam_ho"),
    ("Thêm validate cho form đăng nhập vào code dưới", "lam_ho"),
    ("Vì sao nên dùng bcrypt thay vì sha256 để lưu mật khẩu?", "hoi_khai_niem"),
    ("async/await khác Promise.then ở chỗ nào?", "hoi_khai_niem"),
    ("Index trong database giúp truy vấn nhanh hơn như thế nào?", "hoi_khai_niem"),
    ("CORS là gì, sao trình duyệt chặn request của mình?", "hoi_khai_niem"),
    ("Mình nghĩ lỗi KeyError là do API trả thiếu trường price khi hết hàng, đúng không?", "debug_co_gia_thuyet"),
    ("Có phải test fail vì mình chưa reset database giữa các test không?", "debug_co_gia_thuyet"),
    ("Mình đoán vòng lặp bị chậm vì gọi query trong mỗi lần lặp (N+1), kiểm giúp", "debug_co_gia_thuyet"),
    ("Hình như 401 là do token hết hạn chứ không phải sai secret, mình kiểm thế nào?", "debug_co_gia_thuyet"),
    ("Traceback (most recent call last):\n  File \"app.py\", line 12, in <module>\nKeyError: 'price'", "debug_dan_loi"),
    ("TypeError: Cannot read properties of undefined (reading 'map')", "debug_dan_loi"),
    ("lỗi nè\nsqlite3.OperationalError: database is locked", "debug_dan_loi"),
    ("vẫn lỗi\nModuleNotFoundError: No module named 'flask'", "debug_dan_loi"),
    ("ok cảm ơn", "khac"),
    ("commit giúp mình với message hợp lý", "khac"),
    ("chạy test lại đi", "khac"),
    ("Đổi theme VS Code sang màu tối thế nào?", "khac"),
]

GUARD_CASES = [
    {"id": "gd1", "leaks": True, "why": "có code ≥2 dòng (def, return)",
     "rubric": "Dùng hmac.compare_digest để so sánh thời gian hằng, tránh timing attack.",
     "text": "Bạn có thể viết:\ndef verify(a, b):\n    return hmac.compare_digest(a, b)"},
    {"id": "gd2", "leaks": True, "why": "trùng >50% từ với rubric",
     "rubric": "Dấu ? là tham số hoá truy vấn, giá trị gửi riêng nên chuỗi người dùng không thành câu lệnh SQL.",
     "text": "Dấu ? là tham số hoá truy vấn, giá trị gửi riêng nên chuỗi người dùng không thành câu lệnh SQL."},
    {"id": "gd3", "leaks": False, "why": "gợi ý câu hỏi, không có code, ít trùng rubric",
     "rubric": "Dùng hmac.compare_digest để so sánh thời gian hằng, tránh timing attack.",
     "text": "Thử nghĩ: nếu phép so sánh dừng ngay ở ký tự sai đầu tiên thì kẻ tấn công đo được gì?"},
    {"id": "gd4", "leaks": False, "why": "nhắc tên một hàm trong câu, không phải khối code",
     "rubric": "Salt ngẫu nhiên làm hai người cùng mật khẩu có hash khác nhau, chặn bảng tra sẵn.",
     "text": "Bạn xem lại vai trò của os.urandom(16) trong hash_password: nếu bỏ nó đi thì hai tài khoản cùng mật khẩu sẽ thế nào?"},
    {"id": "gd5", "leaks": True, "why": "code 2 dòng có = và (",
     "rubric": "AbortController huỷ fetch khi quá thời gian, fetch ném AbortError.",
     "text": "Gợi ý: const c = new AbortController();\nsetTimeout(() => c.abort(), 5000);"},
    {"id": "gd6", "leaks": False, "why": "chỉ đường docs, không đáp án",
     "rubric": "OFFSET = (page - 1) * per_page để bỏ qua các trang trước.",
     "text": "Đọc lại phần LIMIT / OFFSET trong docs SQLite rồi tự tính: trang 3, mỗi trang 20 dòng thì bỏ qua bao nhiêu dòng?"},
    {"id": "gd7", "leaks": True, "why": "chép gần nguyên rubric (trùng >50% từ)",
     "rubric": "Cùng order thì cùng idempotency key, cổng thanh toán thấy key đã dùng thì không trừ tiền lần hai.",
     "text": "Đúng ra là: cùng order thì cùng idempotency key, cổng thanh toán thấy key đã dùng nên không trừ tiền lần hai."},
    {"id": "gd8", "leaks": False, "why": "một dòng code đơn lẻ trong câu hỏi (<2 dòng)",
     "rubric": "Debounce huỷ hẹn giờ cũ mỗi lần gõ, chỉ gọi hàm khi ngừng gõ đủ lâu.",
     "text": "Chuyện gì xảy ra với hẹn giờ cũ khi dòng clearTimeout(timer); chạy ở lần gõ phím tiếp theo?"},
]


# ================================================================ chạy

def build():
    rng = random.Random(SEED)
    out, problems = {}, []
    index = {"diffs": {}, "tasks": {}, "sessions": {}, "repos": {}}
    for n, spec in enumerate(REPOS, start=1):
        parsed = {p: parse_annotated(t) for p, t in spec["files"].items()}
        files = {p: after for p, (_, after, _) in parsed.items()}
        ident = {"task_id": spec["name"][:6] + "_t1", "session_id": "s_" + spec["name"][:6], "diff_id": spec["name"][:6] + "_c1"}
        edits = [(spec["edit_after"].get(p, 0), p) for p in files]
        docs_only = all(os.path.splitext(p)[1].lower() in DOC_EXT for p in files)
        if docs_only != (spec.get("skip_reason") == "docs_config"):
            problems.append("%s: cờ docs_config không khớp đuôi file" % spec["name"])
        extra = {"skip_reason": spec.get("skip_reason"), "intent_expected": spec["intent_expected"],
                 "repo": spec["name"]}
        truth, events, probs = finish(rng, "%02d" % n, ident, files, spec["prompts"], edits, spec["branch"],
                                      spec["commit_message"], spec["review_gap"], spec["tool"], "claude-sonnet-5-5", extra)
        truth["open_check"] = bool(truth["open_check_by_size"]) and not spec.get("skip_reason")
        problems += ["%s: %s" % (spec["name"], p) for p in probs]
        diff = "".join(unified_diff(p, before, [c for c, _, _ in after], order) for p, (before, after, order) in parsed.items())
        meta = {"repo": spec["name"], "lang": spec["lang"], "task_id": ident["task_id"], "diff_id": ident["diff_id"],
                "session_id": ident["session_id"], "branch": spec["branch"], "commit_message": spec["commit_message"],
                "description": spec["description"], "files": list(files)}
        out[spec["name"]] = {"events": events, "diff": diff, "meta": meta, "truth": truth,
                             "repo_files": {p: "\n".join(c for c, _, _ in after) + "\n" for p, after in files.items()},
                             "sim_answers": spec["sim_answers"]}
        for key, kind in (("diff_id", "diffs"), ("task_id", "tasks"), ("session_id", "sessions")):
            index[kind][ident[key]] = spec["name"]
        index["repos"][spec["name"]] = spec["name"]
    plan = ["phu_thuoc", "tu_luc", "can_bang", "phu_thuoc", "can_bang"]
    forces = [{}, {}, {}, {"repeat": True}, {"bulk": True, "ai_lines": 58, "review_gap": 200}]
    srng = random.Random(SEED + 1)
    for i in range(1, 41):
        style = plan[i - 1] if i <= len(plan) else srng.choices(list(STYLES), weights=[0.3, 0.4, 0.3])[0]
        name, data, probs = make_session(rng, i, style, forces[i - 1] if i <= len(forces) else None)
        problems += ["%s: %s" % (name, p) for p in probs]
        out["sessions/" + name] = data
        d = "sessions/" + name
        index["sessions"][name] = d
        index["tasks"][name + "_t1"] = d
        index["diffs"][name + "_c1"] = d
    fixtures = {
        "classifier_prompts.json": [{"id": "p%02d" % k, "prompt": p, "label": l} for k, (p, l) in enumerate(CLASSIFIER_PROMPTS, 1)],
        "guard_cases.json": GUARD_CASES,
        "di_sessions.json": [{"session_id": "sess%02d" % k, "task_id": "sess%02d_t1" % k,
                              "di_expected": out["sessions/sess%02d" % k]["truth"]["di"],
                              "features_expected": out["sessions/sess%02d" % k]["truth"]["features"],
                              "tolerance": 5} for k in range(1, 6)],
    }
    return out, index, fixtures, problems


def write_json(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def save(out, index, fixtures):
    for name, d in out.items():
        base = os.path.join(HERE, *name.split("/"))
        os.makedirs(base, exist_ok=True)
        with open(os.path.join(base, "events.jsonl"), "w", encoding="utf-8", newline="\n") as f:
            for e in d["events"]:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
        write_text(os.path.join(base, "diff.patch"), d["diff"])
        write_json(os.path.join(base, "meta.json"), d["meta"])
        write_json(os.path.join(base, "truth.json"), d["truth"])
        if "repo_files" in d:
            for p, text in d["repo_files"].items():
                fp = os.path.join(base, "repo", *p.split("/"))
                os.makedirs(os.path.dirname(fp), exist_ok=True)
                write_text(fp, text)
            write_json(os.path.join(base, "sim_answers.json"), d["sim_answers"])
    write_json(os.path.join(HERE, "index.json"), index)
    os.makedirs(os.path.join(HERE, "fixtures"), exist_ok=True)
    for fname, obj in fixtures.items():
        write_json(os.path.join(HERE, "fixtures", fname), obj)


def report(out):
    print("%-26s %5s %5s %5s %4s  %-28s %s" % ("mẫu", "AIgiu", "AIsua", "nguoi", "DI", "nhắc", "mở Check"))
    for name, d in out.items():
        t = d["truth"]
        s = t["stats"]
        print("%-26s %5d %5d %5d %4d  %-28s %s" % (name, s["ai_giu_nguyen"], s["ai_da_sua"], s["nguoi_viet"], t["di"],
                                                    ",".join(t["nudge_rules"]) or "-", t.get("open_check", t["open_check_by_size"])))
    dis = [d["truth"]["di"] for k, d in out.items() if k.startswith("sessions/")]
    print("40 phiên: DI min %d · trung vị %.0f · max %d · >70: %d · <40: %d"
          % (min(dis), statistics.median(dis), max(dis), sum(x > 70 for x in dis), sum(x < 40 for x in dis)))


def main(argv):
    out, index, fixtures, problems = build()
    report(out)
    if problems:
        print("\nVẤN ĐỀ (%d):" % len(problems))
        for p in problems:
            print("  - " + p)
        return 1
    if "--check" not in argv:
        save(out, index, fixtures)
        print("\nĐã ghi %d mẫu vào data/samples/ (seed %d)." % (len(out), SEED))
    return 0


if __name__ == "__main__":
    for _s in (sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    sys.exit(main(sys.argv[1:]))
