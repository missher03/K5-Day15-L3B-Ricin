import sqlite3


def _escape_like(text: str) -> str:
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def search_products(conn: sqlite3.Connection, keyword: str, page: int = 1, per_page: int = 20):
    page = max(page, 1)
    per_page = min(max(per_page, 1), 100)  # chặn client xin cả triệu dòng một lần
    pattern = "%" + _escape_like(keyword.strip()) + "%"
    sql = (
        "SELECT id, name, price FROM products "
        "WHERE name LIKE ? ESCAPE '\\' "
        "ORDER BY name LIMIT ? OFFSET ?"
    )
    return conn.execute(sql, (pattern, per_page, (page - 1) * per_page)).fetchall()
