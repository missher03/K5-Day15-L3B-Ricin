const jwt = require("jsonwebtoken");

function requireAuth(req, res, next) {
  const header = req.headers.authorization || "";
  const [scheme, token] = header.split(" ");
  if (scheme !== "Bearer" || !token) {
    return res.status(401).json({ error: "thiếu token" });
  }
  try {
    // chỉ nhận HS256 để chặn token giả mạo kiểu alg none
    req.user = jwt.verify(token, process.env.JWT_SECRET, { algorithms: ["HS256"] });
    return next();
  } catch (err) {
    const msg = err.name === "TokenExpiredError" ? "token đã hết hạn" : "token không hợp lệ";
    return res.status(401).json({ error: msg });
  }
}

module.exports = { requireAuth };
