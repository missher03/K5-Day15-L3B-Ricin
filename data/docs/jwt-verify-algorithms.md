# JWT — xác minh token và chỉ định thuật toán
link: https://github.com/auth0/node-jsonwebtoken#jwtverifytoken-secretorpublickey-options-callback
nguon: tóm tắt do nhóm tự viết lại, chưa đối chiếu từng câu với trang gốc

jwt.verify(token, secret, { algorithms: ["HS256"] }) kiểm chữ ký và hạn (exp). Chỉ định algorithms để thư viện không chấp nhận token khai thuật toán khác (vd "none" hoặc đổi kiểu khoá) — lỗ hổng từng gặp ở nhiều thư viện JWT.

Token hết hạn ném TokenExpiredError; chữ ký sai ném JsonWebTokenError. Header thường có dạng "Authorization: Bearer <token>".
