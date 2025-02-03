const express = require("express");
const path = require("path");

const app = express();
const PORT = process.env.PORT || 3000;

// 静的ファイルを「public」ディレクトリから配信
app.use(express.static(path.join(__dirname, "public")));

// ルート ("/") にアクセスしたときに test.html を表示
app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "public", "test.html"));
});

// サーバーを起動
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
