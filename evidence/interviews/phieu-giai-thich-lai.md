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
def split_section(body: str, max_chars: int) -> list[str]:
    """Merge consecutive paragraphs / bullets up to about max_chars; split overly long paragraphs by sentence."""
    units = []
    for para in re.split(r"\n\s*\n", body):
        para = para.strip()
        if not para:
            continue
        if len(para) <= max_chars:
            units.append(para)
            continue
        sentences = re.split(r"(?<=[.;:])\s+(?=[A-ZĐÀ-Ỹ0-9\-])", para) if "\n- " not in para else para.split("\n")
        units.extend(s.strip() for s in sentences if s.strip())
    chunks, cur = [], ""
    for u in units:
        if cur and len(cur) + len(u) + 1 > max_chars:
            chunks.append(cur)
            cur = u
        else:
            cur = f"{cur}\n{u}" if cur else u
    if cur:
        chunks.append(cur)
    return chunks
```

1. Đoạn này làm gì? Giải thích từng bước.
- Hàm này chia văn bản body thành các chunk không vượt quá max_chars ký tự: trước tiên tách theo đoạn văn, đoạn nào dài quá max_chars thì tách nhỏ tiếp thành câu rồi gom vào units, sau đó duyệt units để ghép dần vào cur, cứ sắp tràn max_chars thì đẩy vào chunks và tạo chunk mới.
2. Nếu đổi yêu cầu thành: "Mỗi chunk mới phải giữ lại 1 đơn vị (unit) cuối cùng của chunk trước làm overlap để tránh mất ngữ cảnh khi cắt" thì bạn sửa chỗ nào?
- 2. Sửa trong vòng lặp for u in units:: lưu thêm biến last_u là unit cuối của chunk trước, rồi ở nhánh if sau khi chunks.append(cur) thì gán cur = f"{last_u}\n{u}" thay vì cur = u.
3. Dòng if cur and len(cur) + len(u) + 1 > max_chars: để làm gì, đổi thành if len(cur) + len(u) + 1 > max_chars: (bỏ cur and) thì sao?
- Tôi không rõ vấn đề này lắm

Chấm: một phần 
### E1b

Đoạn code:
```python
def embed_documents(self, texts: list[str], batch: int = 100) -> np.ndarray:
    keys = [hashlib.sha1(t.encode()).hexdigest() for t in texts]
    todo = list({k: t for k, t in zip(keys, texts) if k not in self.cache}.items())
    self.cache_path.parent.mkdir(parents=True, exist_ok=True)
    with self.cache_path.open("a", encoding="utf-8") as f:
        for i in range(0, len(todo), batch):
            part = todo[i:i + batch]
            vecs = self._embed([t for _, t in part], "document")
            for (k, _), v in zip(part, vecs):
                self.cache[k] = v
                f.write(json.dumps({"k": k, "v": v}) + "\n")
            print(f"  embedded {min(i + batch, len(todo))}/{len(todo)}", flush=True)
    return _normalize(np.array([self.cache[k] for k in keys]))
```

1. Đoạn này làm gì? Giải thích từng bước.
- Hàm này embed danh sách texts có cache trên đĩa: tính SHA-1 của từng text làm keys -> lọc ra các (k, t) chưa có trong self.cache (đồng thời khử trùng trong chính texts) -> mở file JSONL ở chế độ append ("a"), gọi API self._embed theo từng lô batch, cập nhật self.cache và ghi thêm vào file -> cuối cùng ghép lại đủ vector theo đúng thứ tự keys ban đầu và chuẩn hóa L2 bằng _normalize.
2. Nếu đổi yêu cầu thành: "Không dùng lại cache cũ mà luôn gọi API embed lại toàn bộ và ghi đè file cache mới" thì bạn sửa chỗ nào?
- Sửa 2 chỗ: Bỏ điều kiện lọc cache cũ (gọi self.cache.clear() ở đầu hoặc bỏ if k not in self.cache ở dòng todo, vẫn giữ dict để khử trùng trong texts). Đổi self.cache_path.open("a", ...) thành self.cache_path.open("w", ...) để ghi đè file cache mới.
3. Dòng todo = list({k: t for k, t in zip(keys, texts) if k not in self.cache}.items()) để làm gì, đổi thành todo = [(k, t) for k, t in zip(keys, texts) if k not in self.cache] thì sao?
- Dòng đó dùng dict comprehension {k: t ...} để vừa lọc những text chưa có trong self.cache, vừa khử trùng các text giống hệt nhau trong cùng danh sách texts. Nếu đổi sang list comprehension [(k, t) ...], các text bị trùng trong texts sẽ bị gọi API embed lặp lại nhiều lần
Chấm: hiểu 
### E1c

Đoạn code:
```python
def rrf(rankings: list[list[str]], k: int = 60) -> dict[str, float]:
    """Reciprocal Rank Fusion: score(d) = sum 1 / (k + rank)."""
    fused: dict[str, float] = defaultdict(float)
    for ranking in rankings:
        for r, cid in enumerate(ranking, 1):
            fused[cid] += 1.0 / (k + r)
    return fused

def search_hybrid(self, query: str, k: int = 20, pool: int = 40) -> list[Hit]:
    b = [h.chunk.chunk_id for h in self.search_bm25(query, pool)]
    v = [h.chunk.chunk_id for h in self.search_vector(query, pool)]
    fused = rrf([b, v], k=settings.rrf_k)
    best = sorted(fused.items(), key=lambda x: -x[1])[:k]
    return [Hit(self.by_id[cid], score, "hybrid") for cid, score in best]
```

1. Đoạn này làm gì? Giải thích từng bước.
- Đoạn này dùng để tìm kiếm hybrid bằng cách gọi BM25 và vector search, sau đó chạy qua hàm rrf để gộp điểm lại, sắp xếp và trả về k kết quả tốt nhất.
2. Nếu đổi yêu cầu thành: "Ưu tiên kết quả từ tìm kiếm vector (ngữ nghĩa) có trọng số gấp đôi BM25 (từ khóa)" thì bạn sửa chỗ nào?
- Mình sẽ tăng pool của search_vector lên gấp đôi (self.search_vector(query, pool * 2))
3. Dòng fused[cid] += 1.0 / (k + r) để làm gì, đổi thành fused[cid] += 1.0 / r (bỏ tham số k) thì sao?
- Tôi nghĩ sẽ bị lỗi
Chấm: Không hiểu

## E2

Người ngoài nhóm (có/không):  có
Ngày:  28/11/2026

### E2a

Đoạn code:
```python
def rerank(self, query: str, hits: list[Hit], top_n: int | None = None) -> list[Hit]:
    if not hits:
        return hits
    scores = self.model.predict([(query, h.chunk.search_text) for h in hits], batch_size=16, show_progress_bar=False)
    out = [Hit(h.chunk, 1 / (1 + math.exp(-float(s))), "rerank") for h, s in zip(hits, scores)]
    out.sort(key=lambda h: -h.score)
    return out[:top_n] if top_n else out
```

1. Đoạn này làm gì? Giải thích từng bước.
- Hàm này dùng model để xếp hạng lại danh sách hits: nếu hits rỗng thì trả về luôn; ngược lại ghép từng cặp (query, h.chunk.search_text) đưa vào self.model.predict để lấy scores, tạo lại danh sách Hit mới với điểm đã chuẩn hóa và nhãn "rerank", sắp xếp giảm dần theo điểm rồi cắt lấy top_n phần tử đầu
2. Nếu đổi yêu cầu thành: "Loại bỏ tất cả các chunk có điểm sau rerank nhỏ hơn 0.5 trước khi lấy top_n" thì bạn sửa chỗ nào?
- Thêm một bước lọc ngay trước dòng return (hoặc sau dòng tạo out)
3. Dòng out = [Hit(h.chunk, 1 / (1 + math.exp(-float(s))), "rerank") for h, s in zip(hits, scores)] để làm gì, đổi thành out = [Hit(h.chunk, float(s), "rerank") for h, s in zip(hits, scores)] thì sao?
- Dòng đó dùng công thức sigmoid để chuẩn hóa điểm dự đoán về khoảng từ 0 đến 1 và gắn vào object Hit. Nếu đổi thành float(s) thì điểm gốc có thể âm hoặc lớn hơn 1 có thể làm lệch cách sắp xếp kết quả.

Chấm: Một phần

### E2b

Đoạn code:
```python
def diversify(ranked, k: int = GRADE_TOP, per_doc: int = MAX_PER_DOC):
    """Top k chunks in rerank order with at most per_doc chunks per document; backfill from the rest if short."""
    out, count, rest = [], {}, []
    for h in ranked:
        if count.get(h.chunk.doc_id, 0) < per_doc:
            out.append(h)
            count[h.chunk.doc_id] = count.get(h.chunk.doc_id, 0) + 1
        else:
            rest.append(h)
        if len(out) == k:
            return out
    return out + rest[:k - len(out)]
```

1. Đoạn này làm gì? Giải thích từng bước.
- Hàm này dùng để lấy ra k chunk từ danh sách ranked cho đa dạng hơn, bằng cách duyệt từng phần tử, dùng count để kiểm tra xem doc_id đã đủ per_doc chưa rồi thêm vào out, còn thừa thì bỏ vào rest.
2. Nếu đổi yêu cầu thành: "Giới hạn tối đa per_doc chunk theo từng danh mục (category) thay vì theo từng tài liệu (doc_id)" thì bạn sửa chỗ nào?
- Tôi nghĩ sửa chữ doc_id ở dòng if count.get(h.chunk.doc_id, 0) < per_doc: thành category là được.
3. Dòng return out + rest[:k - len(out)] để làm gì, đổi thành return out thì sao?
- Dòng đó để nối thêm danh sách rest vào cuối out. Nếu đổi thành return out thì nó không nối phần rest nữa

Chấm: một phần 

### E2c

Đoạn code:

```python
if verdict == "conflict":
    # a conflict only counts when the conflicting chunks come from at least two different documents
    ids = [i for i in grade.get("conflict_ids", []) if i in by_id]
    if len({by_id[i].chunk.doc_id for i in ids}) < 2:
        verdict = "missing_info" if analysis.get("missing_info") else "sufficient"
        grade["relevant_ids"] = list(dict.fromkeys(grade.get("relevant_ids", []) + ids))
        result.trace.append({"step": "check", "override": f"conflict within one document -> {verdict}"})

if verdict == "sufficient":
    accepted = [by_id[i] for i in grade.get("relevant_ids", []) if i in by_id and by_id[i].chunk.status == "active"]
    if not accepted:                                   # grader returned no valid id -> do not answer
        verdict = "no_evidence"
    else:
        result.context_ids = [h.chunk.chunk_id for h in accepted]
        self.generate(ticket, accepted, result, usage, forced=True)
        result.confidence = round(min(conf, result.confidence), 3)
        return
```

1. Đoạn này làm gì? Giải thích từng bước.
- Đoạn này dùng mấy lệnh if để kiểm tra biến verdict xem có bị conflict hay sufficient không rồi gọi self.generate để tạo câu trả lời
2. Nếu đổi yêu cầu thành: "Nếu không có chunk nào active thì vẫn cho phép trả lời dựa trên tài liệu hết hiệu lực, nhưng ghi thêm cảnh báo vào result.reason" thì bạn sửa chỗ nào?
- Tôi không chắc sửa dòng nào cho đúng, chắc phải bỏ đoạn if not accepted
3. Dòng result.confidence = round(min(conf, result.confidence), 3) để làm gì, đổi thành result.confidence = round(max(conf, result.confidence), 3) thì sao?
- Tôi không rõ lắm
Chấm:  chưa hiểu

## E3

Người ngoài nhóm (có/không):  có
Ngày:  28/11/2026

### E3a
Đoạn code:
```python
def to_paragraphs(text: str) -> list[str]:
    """Re-join wrapped PDF lines into logical paragraphs."""
    paragraphs: list[str] = []
    for line in text.split("\n"):
        if not line:
            continue
        if paragraphs and not NEW_PARA_RE.match(line) and not paragraphs[-1].endswith((".", ":", ";", "./.")):
            paragraphs[-1] += " " + line
        elif paragraphs and CHAPTER_RE.match(paragraphs[-1]) and line.isupper():
            paragraphs[-1] += " " + line          # "CHƯƠNG II" + "ĐÀO TẠO ĐẠI HỌC"
        else:
            paragraphs.append(line)
    return paragraphs
```
1. Đoạn này làm gì? Giải thích từng bước.
- Hàm này lấy text cắt theo ký tự xuống dòng \n, rồi duyệt từng dòng để kiểm tra điều kiện và thêm vào list paragraphs để trả về.
2. Nếu đổi yêu cầu thành: "Coi các dòng kết thúc bằng dấu ? hoặc ! cũng là kết thúc đoạn (không nối dòng tiếp theo vào), đồng thời giữ nguyên dòng trống để tách đoạn rõ ràng" thì bạn sửa chỗ nào?
- Mình đoán là cần thêm dấu ? và ! vào biến NEW_PARA_RE ở đâu đó bên ngoài, còn phần giữ dòng trống thì mình không rõ sửa ở dòng nào.
3. Dòng if paragraphs and not NEW_PARA_RE.match(line) and not paragraphs[-1].endswith((".", ":", ";", "./.")): để làm gì, bỏ điều kiện and not paragraphs[-1].endswith((".", ":", ";", "./.")) thì sao?
- Dòng đó dùng để kiểm tra xem đoạn văn có hợp lệ với regex và dấu câu hay không. Nếu bỏ đoạn and not paragraphs[-1].endswith(...) đi thì chắc nó bớt điều kiện kiểm tra dấu câu thôi
Chấm: Chưa hiểu

### E3b
Đoạn code:
```python
def by_paragraph(page: DocumentPage, max_size: int = 1000, strategy: str = "B") -> list[Chunk]:
    """Group whole paragraphs up to `max_size`; always start a new chunk at a
    Chương/Điều heading so one chunk does not mix two articles."""
    groups: list[tuple[dict, list[str]]] = []
    for para in page.metadata["paragraphs"]:
        text = para["text"]
        is_heading = text.startswith(("Điều ", "CHƯƠNG "))
        pieces = _split_long(text, max_size) if len(text) > max_size else [text]
        for i, piece in enumerate(pieces):
            # A chapter title alone is not a useful chunk: attach the first Điều to it.
            if (groups and len(groups[-1][1]) == 1 and groups[-1][1][0].startswith("CHƯƠNG ")
                    and text.startswith("Điều ") and i == 0):
                groups[-1] = (para, groups[-1][1] + [piece])
                continue
            if groups and not (is_heading and i == 0):
                cur_len = sum(len(t) + 1 for t in groups[-1][1])
                same_article = groups[-1][0].get("article") == para.get("article")
                if same_article and cur_len + len(piece) <= max_size:
                    groups[-1][1].append(piece)
                    continue
            groups.append((para, [piece]))
    chunks = []
    for index, (para, texts) in enumerate(groups):
        chunks.append(_make_chunk(strategy, page, index, "\n".join(texts), para,
                                  {"n_paragraphs": len(texts), "articles": [para.get("article")]}))
    return chunks
```
1. Đoạn này làm gì? Giải thích từng bước.
- Hàm này gom các đoạn văn trong một trang thành các chunk không vượt quá max_size: duyệt từng para, nếu dài quá thì tách bằng _split_long, sau đó gộp các đoạn cùng article vào chung nhóm trong groups nếu tổng độ dài vẫn <= max_size (còn gặp Điều/CHƯƠNG thì tách nhóm mới), cuối cùng nối text từng nhóm bằng \n rồi tạo danh sách Chunk.
2. Nếu đổi yêu cầu thành: "Cho phép gộp nhiều Điều ngắn liên tiếp vào chung một chunk miễn là chúng thuộc cùng một chapter và tổng độ dài không vượt quá max_size" thì bạn sửa chỗ nào?
- Mình sẽ sửa dòng same_article = groups[-1][0].get("article") == para.get("article") thành so sánh theo "chapter" (groups[-1][0].get("chapter") == para.get("chapter")) để các đoạn cùng chương có thể gộp vào chung một chunk.
3. Dòng if (groups and len(groups[-1][1]) == 1 and groups[-1][1][0].startswith("CHƯƠNG ") and text.startswith("Điều ") and i == 0): để làm gì, xóa khối if này đi thì sao?
- Khối if đó dùng để gộp luôn Điều đầu tiên vào chung chunk với dòng tiêu đề CHƯƠNG. Nếu xóa đi thì dòng tiêu đề CHƯƠNG sẽ bị đứng một mình thành một chunk riêng rất ngắn, ít thông tin.
Chấm: Một phần

### E3c
Đoạn code:
```python
def _call(self, texts: list[str]) -> list[list[float]]:
    for attempt in range(self.max_retries + 1):
        try:
            start = time.perf_counter()
            response = self.client.embeddings.create(model=self.model_name, input=texts)
            self.api_seconds += time.perf_counter() - start
            self.api_calls += 1
            self.tokens_used += response.usage.total_tokens
            vectors = [item.embedding for item in sorted(response.data, key=lambda d: d.index)]
            bad = {len(v) for v in vectors} - {self.dimensions}
            if bad or len(vectors) != len(texts):
                raise RuntimeError(f"Unexpected embedding shape: dims {bad}, {len(vectors)}/{len(texts)}")
            return vectors
        except (openai.RateLimitError, openai.APIConnectionError, openai.APITimeoutError,
                openai.InternalServerError) as error:
            if attempt == self.max_retries:
                raise
            wait = 2 ** attempt
            print(f"  [embedding] {type(error).__name__}, retry {attempt + 1} in {wait}s")
            time.sleep(wait)
    raise AssertionError("unreachable")
```
1. Đoạn này làm gì? Giải thích từng bước.
- Hàm này dùng để gọi API của OpenAI tạo vectors cho danh sách texts, có bọc try/except trong vòng for để nếu gặp lỗi mạng hay lỗi API thì gọi lại rồi trả về vectors.
2. Nếu đổi yêu cầu thành: "Giới hạn thời gian chờ giữa các lần retry tối đa là 10 giây và chỉ retry tối đa 2 lần cho APITimeoutError" thì bạn sửa chỗ nào?
- Mình sẽ đổi time.sleep(wait) thành time.sleep(10) và sửa self.max_retries thành 2 cho gọn.
3. Dòng vectors = [item.embedding for item in sorted(response.data, key=lambda d: d.index)] để làm gì, đổi thành vectors = [item.embedding for item in response.data] thì sao?
- Dòng đó dùng để lấy các embedding ra khỏi response.data và sắp xếp lại cho đẹp. Nếu bỏ sorted đi thì code gọn hơn và chạy nhanh hơn một chút, chắc không ảnh hưởng gì tới kết quả.
Chấm: Chưa hiểu

## E4

Người ngoài nhóm (có/không):  có
Ngày:  28/11/2026

### E4a
Đoạn code:
```python
def search(self, strategy: str, query_vector: list[float], top_k: int = 3,
           filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    where, params = ["strategy = %s"], [strategy]
    for key, value in (filters or {}).items():
        if key not in FILTERABLE:
            raise ValueError(f"filter key not allowed: {key}")
        values = value if isinstance(value, list) else [value]
        where.append(f"{key} = ANY(%s::{FILTERABLE[key]}[])")
        params.append(values)
    sql = f"""SELECT chunk_id, document_id, source, page, text, metadata,
                     1 - (embedding <=> %s::vector) AS score
              FROM {self.table} WHERE {' AND '.join(where)}
              ORDER BY embedding <=> %s::vector LIMIT %s"""
    qv = np.asarray(query_vector, dtype=np.float32)
    rows = self.conn.execute(sql, [qv, *params, qv, top_k]).fetchall()
    return [{"chunk_id": r[0], "document_id": r[1], "source": r[2], "page": r[3],
             "text": r[4], "metadata": r[5], "score": round(float(r[6]), 6)} for r in rows]
```
1. Đoạn này làm gì? Giải thích từng bước.
- Hàm này tìm kiếm top_k chunk gần nhất với query_vector trong database: duyệt qua filters để ghép thành các điều kiện WHERE, chạy câu SQL tính điểm score từ cột embedding, sắp xếp và giới hạn LIMIT top_k, rồi format từng dòng kết quả thành dict để trả về.
2. Nếu đổi yêu cầu thành: "Chỉ trả về các kết quả có điểm tương đồng score >= 0.75 ngay trong câu lệnh SQL" thì bạn sửa chỗ nào?
- Mình sẽ thêm điều kiện AND score >= 0.75 vào cuối mệnh đề WHERE trong chuỗi sql (trước ORDER BY) để database lọc luôn các kết quả có điểm thấp.
3. Dòng if key not in FILTERABLE: raise ValueError(f"filter key not allowed: {key}") để làm gì, bỏ đoạn kiểm tra này đi thì sao?
- Đoạn đó để kiểm tra xem key trong filters có nằm trong danh sách các cột cho phép FILTERABLE hay không. Nếu bỏ đi mà người dùng truyền key lạ thì xuống dòng dưới tra FILTERABLE[key] sẽ bị lỗi
Chấm: Một phần


### E4b
Đoạn code:
```python
def ingest(store, embedder, chunks, document_ids) -> dict:
    report = {}
    for strategy, items in chunks.items():
        start = time.perf_counter()
        tokens_before = embedder.tokens_used
        existing = store.existing_hashes(strategy)
        changed = [c for c in items if existing.get(c.chunk_id) != c.metadata["content_hash"]]
        vectors = embedder.embed_documents([c.text for c in changed]) if changed else []
        written = store.upsert(strategy, changed, vectors)
        deleted = store.delete_obsolete(strategy, document_ids, [c.chunk_id for c in items])
        report[strategy] = {
            "chunks": len(items), "embedded": len(changed), "skipped_unchanged": len(items) - len(changed),
            "written": written, "deleted_obsolete": deleted, "rows_in_store": store.count(strategy),
            "embedding_tokens": embedder.tokens_used - tokens_before,
            "seconds": round(time.perf_counter() - start, 2),
        }
        print(f"  ingest {strategy}: {report[strategy]}")
    return report
```
1. Đoạn này làm gì? Giải thích từng bước.
- Hàm này dùng để nạp danh sách chunks vào database store theo từng strategy, gọi embedder tạo vector, lưu vào store rồi gom thông số vào dict report để in ra và trả về.
2. Nếu đổi yêu cầu thành: "Thêm tham số force: bool = False; khi force=True thì bỏ qua kiểm tra hash, bắt buộc embed và ghi đè lại toàn bộ các chunk" thì bạn sửa chỗ nào?
- Mình sẽ thêm force: bool = False vào dòng định nghĩa hàm, rồi nếu force là True thì truyền thêm cờ force vào hàm store.upsert hoặc nhờ AI sửa lại giúp đoạn kiểm tra existing.
3. Dòng deleted = store.delete_obsolete(strategy, document_ids, [c.chunk_id for c in items]) để làm gì, xóa dòng này đi thì sao?
- Tôi nghĩ để giải phóng bộ nhờ, tôi cũng không chắc lắm
Chấm: Chưa hiểu

### E4c
Đoạn code:
```python
def _normalize(text: str) -> str:
    """Canonicalize text: NFKC, drop invisible chars, strip accents, collapse spaces."""
    text = unicodedata.normalize("NFKC", text or "")
    text = _INVISIBLE_RE.sub("", text)
    text = text.replace("đ", "d").replace("Đ", "D")
    text = "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )
    # collapse whitespace; also separators used to split words ("i.g.n.o.r.e" is out of scope)
    text = re.sub(r"[\s_]+", " ", text)
    return text.strip().lower()

def detect_injection(user_input: str) -> InputStatus:
    text = _normalize(user_input)

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return "BLOCK"
    return "ALLOW"
```
1. Đoạn này làm gì? Giải thích từng bước.
- Hàm _normalize dùng để làm sạch user_input: chuẩn hóa Unicode, bỏ ký tự ẩn, bỏ dấu tiếng Việt, gộp khoảng trắng/dấu gạch dưới và chuyển về chữ thường. Sau đó detect_injection duyệt qua từng regex trong INJECTION_PATTERNS, nếu re.search khớp thì trả về "BLOCK", không khớp cái nào thì trả về "ALLOW".
2. Nếu đổi yêu cầu thành: "Khi phát hiện injection, trả về cả pattern đã khớp (ví dụ ("BLOCK", pattern)) để ghi vào audit log thay vì chỉ trả về "BLOCK"" thì bạn sửa chỗ nào?
- Mình sẽ sửa trong hàm detect_injection: đổi dòng return "BLOCK" thành return ("BLOCK", pattern) để trả kèm pattern vừa khớp.
3. Dòng text = _INVISIBLE_RE.sub("", text) để làm gì, xóa dòng này đi thì sao?
Dòng đó để xóa các ký tự ẩn (không hiển thị) ra khỏi text. Nếu xóa dòng này đi thì các ký tự lạ/ẩn sẽ vẫn nằm trong chuỗi sau khi chuẩn hóa
Chấm: Một phần

## E5

Người ngoài nhóm (có/không):  có
Ngày:  28/11/2026

### E5a
Đoạn code:
```python
def topic_filter(user_input: str) -> InputStatus:
    input_lower = _normalize(user_input)
    if not input_lower:
        return "BLOCK"

    def _has(topic: str) -> bool:
        return re.search(r"\b" + re.escape(_normalize(topic)), input_lower) is not None

    if any(_has(t) for t in BLOCKED_TOPICS):
        return "BLOCK"
    if not any(_has(t) for t in ALLOWED_TOPICS):
        return "BLOCK"
    return "ALLOW"
```
1. Đoạn này làm gì? Giải thích từng bước.
- Hàm này lọc câu hỏi đúng chủ đề ngân hàng: chuẩn hóa user_input bằng _normalize (rỗng thì "BLOCK" luôn) -> tạo hàm _has(topic) khớp theo ranh giới đầu từ (\b) và re.escape tránh lỗi ký tự đặc biệt -> kiểm tra BLOCKED_TOPICS trước (trúng thì "BLOCK") -> kiểm tra ALLOWED_TOPICS (không trúng từ nào thì "BLOCK") -> còn lại mới "ALLOW".
2. Nếu đổi yêu cầu thành: "Cho phép các câu chào hỏi xã giao (xin chao, hello, cam on) đi qua dù không chứa từ khóa trong ALLOWED_TOPICS, nhưng vẫn chặn nếu chứa BLOCKED_TOPICS" thì bạn sửa chỗ nào?
- Giữ nguyên khối kiểm tra BLOCKED_TOPICS ở đầu; ngay sau đó thêm kiểm tra cho danh sách chào hỏi GREETINGS = ("xin chao", "hello", "cam on"): if any(_has(g) for g in GREETINGS): return "ALLOW" (hoặc kiểm tra ALLOWED_TOPICS + GREETINGS ở dòng if not any(...)).
3. Dòng if any(_has(t) for t in BLOCKED_TOPICS): return "BLOCK" đặt trước kiểm tra ALLOWED_TOPICS để làm gì, nếu đổi thành kiểm tra if any(_has(t) for t in ALLOWED_TOPICS): return "ALLOW" trước rồi mới kiểm tra BLOCKED_TOPICS thì sao?
- Đặt BLOCKED_TOPICS trước để áp dụng nguyên tắc deny-first (ưu tiên chặn). Nếu đảo sang kiểm tra ALLOWED_TOPICS và return "ALLOW" trước thì những câu vừa chứa từ khóa ngân hàng vừa chứa nội dung cấm (ví dụ "How to hack a bank account") sẽ lọt qua bộ lọc.
Chấm: Hiểu


### E5b
Đoạn code:
```python
async def on_user_message_callback(self, *, invocation_context, user_message):
    """Return Content to block, or None to allow."""
    self.total_count += 1
    user_id = getattr(invocation_context, "user_id", None) or "anonymous"
    now = time.time()
    window = self.user_windows[user_id]

    # 1. Drop timestamps that fell out of the sliding window
    while window and window[0] <= now - self.window_seconds:
        window.popleft()

    # 2. Over the limit -> block without calling the LLM
    if len(window) >= self.max_requests:
        wait = max(0.0, self.window_seconds - (now - window[0]))
        self.blocked_count += 1
        return self._block_response(
            f"Rate limit exceeded. Try again in {wait:.0f}s."
        )

    # 3. Within the limit -> record and let it through
    window.append(now)
    return None
```
1. Đoạn này làm gì? Giải thích từng bước.
- Hàm này kiểm tra số lần gửi tin nhắn của từng user_id theo thời gian now, nếu vượt quá self.max_requests thì chặn và báo "Rate limit exceeded", còn không thì trả về None cho đi tiếp.
2. Nếu đổi yêu cầu thành: "Tài khoản có user_id bắt đầu bằng "vip_" được phép gửi gấp đôi max_requests trong cùng window_seconds" thì bạn sửa chỗ nào?
- Mình sẽ thêm if "vip_" in user_id: self.max_requests = self.max_requests * 2 ở đầu hàm để tăng giới hạn cho tài khoản VIP.
3. Dòng window.append(now) đặt ở cuối hàm để làm gì, nếu chuyển dòng này lên ngay trước khối if len(window) >= self.max_requests: thì sao?
- Dòng đó dùng để thêm thời gian now vào danh sách window. Mình nghĩ sẽ chạy nhanh hơn 
Chấm: Chưa hiểu

### E5c
Đoạn code:
```python
def is_egress_allowed(destination: str, payload: str) -> bool:
    # 1. Destination: HTTPS + exact allowlisted host, no embedded credentials / odd port
    try:
        url = urlparse((destination or "").strip())
        host = url.hostname
        port = url.port
    except ValueError:
        return False
    if url.scheme != "https" or host not in ALLOWED_EGRESS_HOSTS:
        return False
    if url.username or url.password or port not in (None, 443):
        return False

    # 2. Payload: deterministic scan for secrets / PII (reuse the CP2 output filter)
    from guardrails.output_guardrails import content_filter

    text = payload if isinstance(payload, str) else json.dumps(payload, default=str)
    if not content_filter(text)["safe"]:
        return False
    if _EXTRA_SENSITIVE.search(text):
        return False
    return True
```
1. Đoạn này làm gì? Giải thích từng bước.
- Hàm này kiểm tra xem có được phép gửi dữ liệu ra ngoài không: đầu tiên tách URL destination để kiểm tra có dùng https và thuộc ALLOWED_EGRESS_HOSTS không, sau đó đưa payload qua content_filter để kiểm tra an toàn rồi trả về True hoặc False
2. Nếu đổi yêu cầu thành: "Chỉ cho phép gửi dữ liệu tới các endpoint có đường dẫn (url.path) bắt đầu bằng /v1/ và giới hạn kích thước text tối đa 10.000 ký tự" thì bạn sửa chỗ nào?
- Thêm 2 điều kiện if: kiểm tra if not url.path.startswith("/v1/"): return False ở phần kiểm tra URL, và if len(payload) > 10000: return False ở phần kiểm tra payload.
3. Dòng if url.scheme != "https" or host not in ALLOWED_EGRESS_HOSTS: để làm gì, đổi điều kiện kiểm tra host thành not any(host.endswith(h) for h in ALLOWED_EGRESS_HOSTS) thì sao?
- Dòng đó dùng để đảm bảo URL phải là https và host phải nằm trong danh sách ALLOWED_EGRESS_HOSTS. Nếu đổi sang endswith(h) thì kiểm tra sẽ thoáng hơn
Chấm: Một phần