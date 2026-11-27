/**
 * Tạo Google Form khảo sát CodeOwn (Nhóm Ricin) — nội dung khớp evidence/survey/questions.md.
 * Cách chạy: script.google.com → New project → dán file này → chọn createCodeOwnSurvey → Run.
 * Link form in ra ở Execution log.
 */
function createCodeOwnSurvey() {
  var form = FormApp.create('Lập trình viên mới dùng công cụ AI viết code: chuyện thực tế tuần qua (4–6 phút)');
  form.setDescription(
    'Chào bạn, nhóm mình (sinh viên khoá AI20K) đang tìm hiểu cách lập trình viên mới làm việc với code do ' +
    'công cụ AI (Copilot, Cursor, ChatGPT, Claude…) viết. Các câu hỏi chỉ hỏi về NHỮNG GÌ ĐÃ XẢY RA trong ' +
    'tuần / tháng vừa qua, không có đúng sai. Form không thu tên hay email. Câu trả lời chỉ dùng tổng hợp ' +
    'số liệu cho bài hackathon. Cảm ơn bạn!');
  form.setCollectEmail(false);
  form.setProgressBar(true);
  form.setAllowResponseEdits(false);
  form.setConfirmationMessage('Cảm ơn bạn đã dành thời gian! Câu trả lời của bạn giúp nhóm rất nhiều.');

  var num = function (max) {
    return FormApp.createTextValidation().setHelpText('Nhập một số từ 0 đến ' + max)
      .requireNumberBetween(0, max).build();
  };
  var mc = function (title, choices, required, help) {
    var it = form.addMultipleChoiceItem().setTitle(title).setChoiceValues(choices).setRequired(required !== false);
    if (help) it.setHelpText(help);
    return it;
  };
  var cb = function (title, choices, required) {
    return form.addCheckboxItem().setTitle(title).setChoiceValues(choices).showOtherOption(true)
      .setRequired(required !== false);
  };
  var para = function (title, help) {
    var it = form.addParagraphTextItem().setTitle(title).setRequired(false);
    if (help) it.setHelpText(help);
    return it;
  };

  // ---------- Trang 1: A1 (rẽ nhánh junior / senior) ----------
  var a1 = form.addMultipleChoiceItem()
    .setTitle('A1. Bạn đã lập trình có trả lương / thực tập / làm đồ án thật được bao lâu?')
    .setRequired(true);

  // ---------- Trang 2: Phần A tiếp ----------
  var pA = form.addPageBreakItem().setTitle('Phần A — Về bạn');
  mc('A2. Hiện tại bạn là:', [
    'Sinh viên IT năm 1–2',
    'Sinh viên IT năm 3–4 / làm đồ án tốt nghiệp',
    'Fresher / junior đang đi làm',
    'Người tự học / chuyển ngành sang lập trình',
    'Khác']);
  var a3 = form.addMultipleChoiceItem()
    .setTitle('A3. Trong 1 tháng qua, bạn dùng công cụ AI để viết / sửa code bao thường xuyên?')
    .setRequired(true);
  cb('A4. Bạn đã dùng công cụ nào trong tháng qua?', [
    'GitHub Copilot', 'Cursor', 'Claude Code',
    'ChatGPT / Claude / Gemini trên web (copy–paste)', 'Windsurf / Cline / Codex'], false);

  // ---------- Trang 3: Phần B ----------
  form.addPageBreakItem().setTitle('Phần B — Chuyện tuần / tháng vừa qua')
    .setHelpText('Hãy nghĩ về những lần thật sự đã xảy ra. Không nhớ chính xác thì ước lượng.');
  form.addTextItem()
    .setTitle('B1. Tuần vừa qua, bạn làm bao nhiêu task (bài tập, ticket, tính năng, bug) có dùng AI để viết code?')
    .setValidation(num(100)).setRequired(true);
  mc('B2. Nghĩ về lần nộp gần nhất (commit / PR / bài nộp) có code AI viết. Khoảng bao nhiêu phần code trong đó là AI viết và bạn giữ gần như nguyên?',
    ['Dưới 25%', '25–50%', '50–75%', 'Trên 75%', 'Không nhớ']);
  mc('B3. Trước khi nộp lần đó, bạn đã đọc phần code AI viết tới mức nào?',
    ['Đọc kỹ từng dòng', 'Đọc lướt phần chính', 'Chạy thử thấy chạy được là nộp, gần như không đọc', 'Không nhớ']);
  mc('B4. Trong lần nộp gần nhất đó, có đoạn code quan trọng nào (xử lý lỗi, truy vấn DB, đăng nhập, gọi API…) mà đến giờ bạn vẫn không giải thích được nó làm gì hoặc vì sao viết như vậy không?',
    ['Có, ít nhất 1 đoạn', 'Không chắc', 'Không, giải thích được hết']);
  mc('B5. Trong 1 tháng qua, bao nhiêu lần có người (reviewer, giảng viên, người phỏng vấn, đồng đội) hỏi bạn về một đoạn code AI viết mà bạn không trả lời được?',
    ['0', '1 lần', '2–3 lần', '4 lần trở lên', 'Không nhớ']);
  mc('B6. Tuần vừa qua, bao nhiêu lần bạn dán nguyên thông báo lỗi vào AI trước khi tự đọc / đoán nguyên nhân?',
    ['0', '1–3 lần', '4–10 lần', 'Trên 10 lần']);
  mc('B7. Trong 1 tháng qua, bao nhiêu lần bài / PR của bạn bị trả lại hoặc phải làm lại vì code AI viết có chỗ sai mà bạn không hiểu?',
    ['0', '1 lần', '2–3 lần', '4 lần trở lên', 'Không nhớ']);
  mc('B8. Lần gần nhất bạn kẹt vì không hiểu code AI viết, bạn mất bao lâu để gỡ được?',
    ['Chưa gặp trong tháng qua', 'Dưới 15 phút', '15–30 phút', '30–60 phút', '1–2 giờ', 'Trên 2 giờ / bỏ luôn']);
  cb('B9. Lần đó bạn đã xoay xở thế nào?', [
    'Hỏi lại / dán lỗi lại cho AI', 'Hỏi senior / bạn bè', 'Tự đọc docs / Stack Overflow',
    'Tự debug từng dòng', 'Xoá đi, nhờ AI viết lại từ đầu', 'Bỏ qua, chưa giải quyết', 'Chưa gặp']);
  para('B10. (Tuỳ chọn) Kể ngắn lần gần nhất đó: bạn đang làm gì, kẹt ở đâu, ai phát hiện, hậu quả ra sao?',
    'Đừng ghi tên công ty, tên người hay đoạn code bí mật.');

  // ---------- Trang 4: Phần C (tuỳ chọn) ----------
  form.addPageBreakItem().setTitle('Phần C — (Tuỳ chọn, ~3 phút) Thử giải thích 2 đoạn code ngắn')
    .setHelpText('Không bắt buộc và không phải bài kiểm tra. Trả lời bằng lời theo cách hiểu của bạn, ' +
      'KHÔNG cần tra Google / hỏi AI. Không biết thì ghi "không biết" — vậy cũng rất có ích. Bỏ trống để qua trang sau.');
  form.addSectionHeaderItem().setTitle('Đoạn 1 (Python)').setHelpText(
    'def verify_password(password: str, stored: str) -> bool:\n' +
    '    salt_hex, digest_hex = stored.split("$", 1)\n' +
    '    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 200_000)\n' +
    '    return hmac.compare_digest(digest.hex(), digest_hex)');
  para('C1. Dòng cuối so sánh hash bằng hmac.compare_digest. Vì sao không dùng == ?');
  para('C2. Mật khẩu được lưu kèm salt (sinh ngẫu nhiên lúc tạo tài khoản). Bỏ salt đi thì sao?');
  form.addSectionHeaderItem().setTitle('Đoạn 2 (JavaScript)').setHelpText(
    'const res = await fetch(url, { signal: controller.signal });\n' +
    'if (res.status >= 500) throw new Error(`server ${res.status}`);   // nhảy xuống catch để thử lại\n' +
    'if (!res.ok) return { error: `HTTP ${res.status}` };              // 4xx: trả luôn\n' +
    '// ... trong catch:\n' +
    'await new Promise((r) => setTimeout(r, 500 * 2 ** attempt));');
  para('C3. Vì sao chỉ thử lại khi status ≥ 500, còn lỗi 4xx thì trả về luôn?');
  para('C4. Vì sao thời gian chờ trước lần thử tiếp lại tăng dần (500 ms, 1 s, 2 s…)?');

  // ---------- Trang 5: Kết thúc (junior) ----------
  form.addPageBreakItem().setTitle('Gần xong rồi!');
  form.addTextItem().setRequired(false).setTitle(
    'E1. (Tuỳ chọn) Bạn có sẵn lòng cho nhóm hỏi thêm 10–15 phút, hoặc dùng thử một công cụ nhỏ trên VS Code vào sáng 28/11 không? Nếu có, để lại cách liên hệ (Zalo / Telegram / email).');

  // ---------- Trang 6: Phần D (senior) — sau trang 5 thì gửi form ----------
  var pD = form.addPageBreakItem().setTitle('Phần D — Dành cho người trên 2 năm kinh nghiệm')
    .setGoToPage(FormApp.PageNavigationType.SUBMIT); // trang 5 (trước break này) xong → gửi form
  mc('D1. Bạn có review code của lập trình viên ≤2 năm kinh nghiệm không?',
    ['Có, thường xuyên', 'Thỉnh thoảng', 'Không']);
  form.addTextItem()
    .setTitle('D2. Trong 1 tháng qua, bao nhiêu PR / bài của junior mà bạn phải hỏi lại vì họ không giải thích được code (nghi do AI viết)?')
    .setValidation(num(200)).setRequired(true);
  mc('D3. Mỗi lần như vậy bạn mất thêm khoảng bao lâu (hỏi, giải thích, review lại)?',
    ['Dưới 15 phút', '15–30 phút', '30–60 phút', 'Trên 1 giờ']);
  para('D4. (Tuỳ chọn) Kể ngắn trường hợp gần nhất.', 'Đừng ghi tên công ty, tên người.');
  form.addTextItem().setRequired(false).setTitle(
    'D5. (Tuỳ chọn) Bạn có sẵn lòng cho nhóm hỏi thêm 15 phút qua call không? Nếu có, để lại cách liên hệ.');

  // ---------- Rẽ nhánh ----------
  a1.setChoices([
    a1.createChoice('Chưa đi làm, đang là sinh viên', pA),
    a1.createChoice('Dưới 6 tháng', pA),
    a1.createChoice('6–12 tháng', pA),
    a1.createChoice('1–2 năm', pA),
    a1.createChoice('Trên 2 năm', pD)
  ]);
  a3.setChoices([
    a3.createChoice('Hầu như mỗi ngày', FormApp.PageNavigationType.CONTINUE),
    a3.createChoice('Vài lần mỗi tuần', FormApp.PageNavigationType.CONTINUE),
    a3.createChoice('Vài lần trong tháng', FormApp.PageNavigationType.CONTINUE),
    a3.createChoice('Không dùng', FormApp.PageNavigationType.SUBMIT)
  ]);

  Logger.log('Link sửa form: ' + form.getEditUrl());
  Logger.log('Link gửi đi:  ' + form.getPublishedUrl());
}
