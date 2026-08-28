
// 监听输入框的按键事件，用户按下回车触发查询
document.getElementById("searchInput").addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
        const query = e.target.value.trim();
        if (!query) return; // 如果输入为空则不发送请求

        const resultBox = document.getElementById("searchResults");
        resultBox.innerHTML = "正在查询，请稍候..."; // 显示查询中

        // 发送POST请求到后端
        fetch("/search", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ query: query })
        })
            .then(res => res.json())
            .then(data => {
                // 将结果显示到页面上
                resultBox.innerHTML = data.result.replace(/\n/g, "<br>");
            })
            .catch(() => {
                // 请求出错时显示错误信息
                resultBox.innerHTML = "发生错误，请稍后重试。";
            });
    }
});