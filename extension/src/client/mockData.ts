import { CheckQuestion, LedgerItem, NudgeHistoryItem, PendingNudge } from "../types";

export const INITIAL_PENDING_NUDGE: PendingNudge = {
  id: "ndg_01",
  rule: "same_error_3x",
  message: "Bạn vừa dán cùng một lỗi 3 lần mà chưa sửa dòng nào. Bạn nghĩ lỗi do đâu?",
  metric_text: "3 lần liên tiếp · 0 dòng tự sửa",
  ts: "2026-11-27T20:18:00+07:00"
};

export const INITIAL_LEDGER_ITEMS: LedgerItem[] = [
  {
    ts: "2026-11-27T14:10:00+07:00",
    task_id: "t_20261127_00",
    concept: "So sánh mật khẩu thời gian hằng",
    label: "mot_phan",
    next_step: "Đọc docs hmac.compare_digest"
  },
  {
    ts: "2026-11-26T21:00:00+07:00",
    task_id: "t_20261126_02",
    concept: "async / await trong FastAPI",
    label: "chua_hieu",
    next_step: "Làm bài tập nhỏ 15 phút"
  },
  {
    ts: "2026-11-26T19:15:00+07:00",
    task_id: "t_20261126_01",
    concept: "Mã lỗi HTTP 404 và 204",
    label: "hieu"
  }
];

export const INITIAL_NUDGES: NudgeHistoryItem[] = [
  {
    ts: "2026-11-27T14:02:00+07:00",
    rule: "lam_ho",
    summary: "Nhờ AI viết cả endpoint xoá todo",
    action: "dismiss"
  }
];

export const MOCK_QUESTIONS: CheckQuestion[] = [
  {
    qid: "q1",
    file: "app/routes.py",
    lines: [41, 42],
    concept: "Xử lý ca không tìm thấy bản ghi",
    question: "Nếu bỏ hai dòng kiểm tra `todo is None`, lỗi xảy ra ở dòng nào và client nhận mã HTTP gì?"
  },
  {
    qid: "q2",
    file: "app/routes.py",
    lines: [45, 45],
    concept: "Mã HTTP 204 No Content",
    question: "Vì sao route xoá bản ghi trả về mã 204 thay vì 200 kèm nội dung JSON?"
  },
  {
    qid: "q3",
    file: "app/routes.py",
    lines: [39, 44],
    concept: "Vòng đời Session SQLAlchemy",
    question: "`Depends(get_db)` đóng session ở thời điểm nào và điều gì xảy ra nếu `db.commit()` ném ngoại lệ?"
  }
];

export const MOCK_REFLECT_MARKDOWN = [
  "# Báo cáo Task t_20261127_01 · feat/todo-delete",
  "",
  "## Diễn biến chính",
  "- Nhờ AI tạo endpoint xoá todo [log#ev_01]",
  "- Dán lỗi session 3 lần trước khi nêu giả thuyết [log#ev_04]",
  "- Hoàn thành Check sau commit 3f2a1c9 [app/routes.py:41-45]",
  "",
  "## Cần học tiếp",
  "- Vòng đời Session SQLAlchemy trong FastAPI [docs:fastapi-dependencies]",
  "- Xử lý mã lỗi HTTP 404 vs 500 [app/routes.py:41-42]"
].join("\n");
