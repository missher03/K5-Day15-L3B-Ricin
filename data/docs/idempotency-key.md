# Idempotency key — chống trừ tiền hai lần
link: https://docs.stripe.com/api/idempotent_requests
nguon: tóm tắt do nhóm tự viết lại, chưa đối chiếu từng câu với trang gốc

Idempotency key là một mã gửi kèm yêu cầu thanh toán. Cùng một key gửi lại nhiều lần (bấm hai lần, mạng chập chờn tự gửi lại) thì phía cổng thanh toán chỉ thực hiện một lần và trả lại kết quả cũ.

Key nên gắn với thứ chỉ xảy ra một lần (vd mã đơn hàng), không sinh ngẫu nhiên mỗi lần bấm.
