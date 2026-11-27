"""Chặn lộ đáp án bằng code: chạy trên `hint` và `follow_up` trước khi tới người dùng (Q8).

Lộ đáp án = có code ≥2 dòng liền, hoặc >50% từ nội dung của câu nằm trong rubric ẩn.
"""
import re
import unicodedata

# shortcut: danh sách stopword viết tay, ngắn; thêm từ khi gặp ca bắt nhầm sau lượt 1.
STOPWORDS = frozenset("""
là và của có không thì mà cho với các những một được này đó khi nếu để trong ra vào lại đã sẽ
đang bị từ theo như hay hoặc nào gì sao vì nên rồi cũng thế đây kia ở trên dưới bạn mình tôi
nó họ ta đi làm thử nghĩ xem chỗ cái việc điều gì thế nào bao nhiêu
the a an of to in on for and or is are be it this that with as by at from if not what why how
""".split())

_CODE_START = re.compile(
    r"^\s*(def|class|return|import|from|elif|else|for|while|try|except|finally|with|raise|"
    r"const|let|var|function|public|private|SELECT|INSERT|UPDATE|DELETE)\b|^\s*if\b.*:\s*$")
_FENCE = "```"


def _norm(text):
    return unicodedata.normalize("NFC", text or "").lower()


def _words(text):
    return [w for w in re.findall(r"\w+", _norm(text)) if w not in STOPWORDS and not w.isdigit()]


def _code_like(line):
    s = line.rstrip()
    if not s.strip():
        return False
    return s.startswith(("    ", "\t")) or s.endswith((":", ";", "{", "}")) or bool(_CODE_START.match(s))


def has_code(text):
    if _FENCE in (text or ""):
        return True
    run = 0
    for line in (text or "").splitlines():
        run = run + 1 if _code_like(line) else 0
        if run >= 2:
            return True
    return False


def rubric_overlap(text, rubric):
    """Tỉ lệ từ nội dung của `text` có trong rubric (0..1)."""
    words = _words(text)
    if not words:
        return 0.0
    vocab = set(_words(rubric))
    return sum(1 for w in words if w in vocab) / len(words)


def leaks_answer(text, rubric):
    if not text:
        return False
    return has_code(text) or rubric_overlap(text, rubric) > 0.5


def safe_hint(concept=None, lines=None):
    """Gợi ý mức 1 viết bằng mẫu cố định: không tốn token, không thể lộ đáp án (Q18)."""
    where = "dòng %d–%d" % (lines[0], lines[1]) if lines else "đoạn code này"
    hint = "Thử đọc lại %s: đoạn này xử lý trường hợp nào, và nếu bỏ nó đi thì chuyện gì xảy ra?" % where
    if concept:
        hint += " Liên quan tới: %s." % concept
    return hint
