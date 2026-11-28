# Thử "giải thích lại" CodeOwn

Mỗi người 3 đoạn code AI viết cho chính họ gần đây (có rẽ nhánh / truy vấn / xử lý lỗi). Gõ câu trả lời nguyên văn sau `Trả lời:`. Không ghi tên thật.

Cách chấm:  
- **hiểu**: giải thích đúng và chỉ ra đúng chỗ cần sửa  
- **một phần**: đúng ý chính nhưng sai hoặc thiếu chi tiết  
- **chưa hiểu**: chỉ đọc lại code, hoặc không trả lời được

## E1

Người ngoài nhóm (có/không):  có
Ngày:  28/11/2026

### E1a

Đoạn code:
```python
def check_password(raw, stored_hash, salt):
    digest = hashlib.pbkdf2_hmac("sha256", raw.encode(), salt, 100_000)
    return hmac.compare_digest(digest, stored_hash)
```

1. Đoạn này làm gì? Giải thích từng bước.  
Trả lời:Băm mật khẩu nhập vào bằng PBKDF2 với cùng salt và 100.000 vòng, rồi so với hash đã lưu.

2. Nếu đổi yêu cầu thành: "khoá tài khoản sau 5 lần sai" thì bạn sửa chỗ nào?  
Trả lời:Khoá sau 5 lần sai thì phải đếm số lần sai theo user ở chỗ gọi hàm này, không sửa trong hàm.

3. Dòng `hmac.compare_digest` để làm gì, đổi thành `==` thì sao?
Trả lời:Tôi cũng không rõ lắm

Chấm: một phần 
### E1b

Đoạn code:
```python
cur.execute("UPDATE items SET name = ? WHERE id = ?", (name, item_id))
if cur.rowcount == 0:
    abort(404)
```

1. Đoạn này làm gì? Giải thích từng bước.  
Trả lời:Cập nhật item, không có thì báo 404. `?` để chống SQL injection.

2. Nếu đổi yêu cầu thành "chỉ chủ sở hữu được sửa" thì sửa chỗ nào?
Trả lời:Thêm `AND owner_id = ?` vào WHERE và truyền id người đang đăng nhập.
3. Dấu `?` để làm gì, ghép chuỗi bằng f-string thì sao? 
Trả lời: `?` để chống SQL injection.

Chấm: hiểu 
### E1c

Đoạn code:
```js
async function fetchUser(id, retries = 2) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), 3000);
  try {
    const res = await fetch(`/api/users/${id}`, { signal: ctrl.signal });
    if (!res.ok) throw new Error(res.status);
    return await res.json();
  } catch (e) {
    if (retries > 0) return fetchUser(id, retries - 1);
    throw e;
  } finally { clearTimeout(t); }
}
```

1. Đoạn này làm gì? Giải thích từng bước.  
Trả lời:Gọi API có timeout 3 giây và retry.
2. Nếu đổi yêu cầu thành "không thử lại khi lỗi 404" thì sửa chỗ nào? 
Trả lời:404 thì sửa điều kiện retries.
3. `finally { clearTimeout(t) }` để làm gì, bỏ đi thì sao?
Trả lời: clearTimeout để dọn dẹp.

Chấm: một phần 

## E2

Người ngoài nhóm (có/không):  có
Ngày:  28/11/2026

### E2a

Đoạn code:
```python
with open(path, encoding="utf-8-sig", newline="") as f:
    rows = [r for r in csv.DictReader(f) if r.get("email")]
```

1. Đoạn này làm gì?   
Trả lời:Đọc CSV thành danh sách dict, bỏ dòng không có email.

2. Nếu đổi yêu cầu thành "bỏ qua email trùng" thì sửa chỗ nào?
Trả lời:Trùng thì dùng set

3. `encoding="utf-8-sig"` để làm gì, đổi thành `"utf-8"` thì sao?
Trả lời: Encoding để đọc tiếng Việt.

Chấm: hiểu 

### E2b

Đoạn code:
```js
const payload = jwt.verify(token, process.env.JWT_SECRET, { algorithms: ["HS256"] });
req.user = payload.sub;
```

1. Đoạn này làm gì? Giải thích từng bước.  
Trả lời:Kiểm chữ ký token bằng khoá bí mật, đúng thì gắn id người dùng vào request.

2. Nếu đổi yêu cầu thành "token hết hạn thì trả 401" thì sửa chỗ nào? 
Trả lời:Bọc `verify` trong try/catch, bắt lỗi hết hạn thì trả 401.
3. `{ algorithms: ["HS256"] }` để làm gì, bỏ đi thì sao?
Trả lời:Tôi nghĩ có thể sẽ bị lỗi

Chấm: một phần 

### E2c

Đoạn code:

```python
page = max(int(request.args.get("page", 1)), 1)
items = db.query(Item).offset((page - 1) * 20).limit(20).all()
```

1. Đoạn này làm gì? Giải thích từng bước.  
Trả lời:Lấy page rồi query có offset limit.

2. Nếu đổi yêu cầu thành "cho người dùng chọn số dòng mỗi trang, tối đa 100" thì sửa chỗ nào?
Trả lời:Tôi cũng không chắc lắm , chắc sẽ sửa offset

3. `max(..., 1)` để làm gì, bỏ đi thì sao?
Trả lời: Tôi không rõ lắm

Chấm:  chưa hiểu

