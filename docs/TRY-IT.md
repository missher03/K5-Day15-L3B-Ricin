# Tự thử CodeOwn trong 15 phút

Hướng dẫn cho người chưa biết repo: cài, mở extension CodeOwn trong VS Code, để AI viết code, commit rồi trả lời Check. Lệnh viết cho **Windows PowerShell**. macOS / Linux thay `python` bằng `python3`, đường dẫn `C:\...` bằng `~/...`.

## 1. Cần có

| Thứ | Ghi chú |
|---|---|
| VS Code ≥ 1.85 | có lệnh `code` trong terminal (VS Code: `Ctrl+Shift+P` → *Shell Command: Install 'code' command in PATH* nếu chưa có) |
| Python 3.10+ | Windows gõ `python --version`; không có thì cài từ python.org, tick *Add python.exe to PATH* |
| Node.js 18+ và npm | để biên dịch extension |
| Git | |
| Claude Code | công cụ AI để thử hook. Cursor: xem mục 7 |
| API key Anthropic | không có key vẫn chạy được **chế độ giả**, nhưng Check sẽ không có câu hỏi thật |

## 2. Lấy code và đặt API key

```powershell
cd $HOME
git clone https://github.com/missher03/K5-Day15-L3B-Ricin.git
cd K5-Day15-L3B-Ricin
copy .env.example .env        # macOS / Linux: cp .env.example .env
notepad .env
```

Điền trong `.env` (cấu hình nhóm đã dùng cho eval):

```
MODEL_PROVIDER=anthropic
API_KEY=<key của bạn>
CODEOWN_MODEL_SMALL=claude-haiku-5-5
CODEOWN_MODEL_STRONG=claude-sonnet-5-5
CODEOWN_SECOND_JUDGE=1
```

- **Không commit `.env`**, không dán key vào code / ảnh chụp. `.env` đã có trong `.gitignore`.
- Lõi Python chỉ dùng thư viện chuẩn, không cần `pip install`.

Biên dịch extension:

```powershell
cd extension
npm install
npm run compile
cd ..
```

## 3. Tạo repo thử và cài hook

```powershell
$K = "$HOME\K5-Day15-L3B-Ricin"          # repo CodeOwn
$C = "$K\codebase\codeown_cli.py"
mkdir $HOME\codeown-try ; cd $HOME\codeown-try
git init
python $C init --repo . --tools claude_code
```

Kết quả đúng: `hooks_written ['.claude/settings.json', '.git/hooks/post-commit']`. Hook ghi lại prompt và file Claude Code sửa vào `.codeown/` (chỉ nằm trên máy, đã thêm vào `.gitignore`).

Báo extension biết lõi Python ở đâu: tạo `.vscode\settings.json` trong repo thử:

```powershell
mkdir .vscode -Force
@"
{
  "codeown.corePath": "$($K -replace '\\','\\')\\codebase",
  "codeown.pythonPath": "python"
}
"@ | Set-Content .vscode\settings.json -Encoding utf8
type .vscode\settings.json
```

(macOS / Linux: `"codeown.pythonPath": "python3"` và `corePath` là đường dẫn tuyệt đối tới thư mục `codebase`.)

## 4. Mở VS Code có extension

Extension chưa đóng gói `.vsix`, nên mở VS Code ở chế độ phát triển:

```powershell
code -n --extensionDevelopmentPath="$K\extension" "$HOME\codeown-try"
```

Đúng thì thanh bên trái có biểu tượng **CodeOwn** và thanh trạng thái dưới cùng có chữ CodeOwn / DI.

## 5. Kịch bản thử 5 phút

1. Trong cửa sổ đó mở terminal, chạy `claude` (mở **sau** bước 3 để Claude Code nạp hook).
2. Nhờ Claude viết một file có rẽ nhánh / xử lý lỗi, **≥ 20 dòng** (Check chỉ mở khi ≥20 dòng AI hoặc ≥30% diff là AI), ví dụ: *"Viết auth.py: băm mật khẩu bằng pbkdf2 có salt, so sánh bằng hmac.compare_digest, khoá tài khoản sau 5 lần sai"*.
3. Kiểm hook đã ghi: `python $C log --last 10` → thấy `claude_code prompt` và `claude_code AI sửa file auth.py (+N dòng)`.
4. Commit: `git add . ; git commit -m "login"`. Xem mức phụ thuộc: `python $C status --repo .`.
5. `Ctrl+Shift+P` → **CodeOwn: Mở Check** → 2–5 câu hỏi, mỗi câu trỏ `file:dòng`.
6. Trả lời mơ hồ ("để bảo mật") → thường bị chấm *Chưa hiểu / Một phần* kèm gợi ý, không lộ đáp án. Trả lời lại bằng lời của mình cho đúng cơ chế → *Hiểu*. Dán lại code → bị yêu cầu tự giải thích. Nút **Sang câu tiếp theo** để chuyển câu bất kỳ lúc nào.
7. Xong câu cuối → báo cáo **Reflect** có nguồn từng ý → bấm lưu vào **Sổ kiến thức** (`CodeOwn: Mở Sổ kiến thức`).

## 6. Thử không cần extension

```powershell
cd $HOME\K5-Day15-L3B-Ricin
python run.py                 # gõ: examine repo03_c1  (ca mẫu có sẵn: hỏi 3 câu về đăng nhập)
```

Hoặc trọn luồng trong terminal trên repo thử (sau khi commit ở bước 5.4):

```powershell
cd $HOME\codeown-try
python $C task show --repo .            # lấy task_id
python $C done --task <task_id>         # hỏi từng câu, chấm, in Reflect, hỏi có lưu Sổ không
```

## 7. Lỗi thường gặp

| Gặp | Làm |
|---|---|
| `log` không có dòng `claude_code` | Claude Code mở trước khi chạy `init` → thoát Claude Code, mở lại trong repo thử |
| Check báo bỏ qua / 0 câu hỏi | diff dưới ngưỡng (<20 dòng AI và <30%), hoặc diff chỉ đổi docs / định dạng / tên biến — đúng thiết kế |
| Câu hỏi có chữ "[câu hỏi giả]", Reflect ghi "[báo cáo giả]" | `.env` chưa có `MODEL_PROVIDER` / `API_KEY` → đang chạy chế độ giả |
| Extension báo không chạy được Python | Windows không có `python3`: đặt `"codeown.pythonPath": "python"` (hoặc `py`) |
| Mất biểu tượng CodeOwn sau khi tắt VS Code | chạy lại lệnh `code -n --extensionDevelopmentPath=...` ở mục 4; sửa code extension thì `npm run compile` rồi `Developer: Reload Window` |
| Gõ `python` mở Microsoft Store | dùng `py` thay `python` |

## 8. Giới hạn hiện tại

- Hook có cho **Claude Code** (đã thử) và **Cursor** (`init --tools cursor`, ghi `.cursor/hooks.json`; mới thử bằng dữ liệu mô phỏng, **chưa kiểm chứng trong Cursor thật**). **GitHub Copilot, Codex: chưa làm**, code do hai công cụ này viết sẽ bị tính là tự viết.
- Extension chỉ chạy ở chế độ phát triển (chưa có `.vsix` trên Marketplace).
- Chấm câu trả lời gọi model thật (~0,03 USD / task theo `cost/cost-estimate.md`), người dùng tự trả bằng API key của mình. Log, code và Sổ chỉ nằm trong `.codeown/` trên máy, không gửi lên server.
