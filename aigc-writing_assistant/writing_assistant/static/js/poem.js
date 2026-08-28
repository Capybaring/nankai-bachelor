document.addEventListener('DOMContentLoaded', function () {
    // 获取诗词输入元素
    const poemTitleInput = document.getElementById('poemTitle');
    const poemContentInput = document.getElementById('poemContent');
    const submitBtn = document.getElementById('submitPoem');
    const errorMessage = document.getElementById('errorMessage');

    // 获取DOM元素
    const poemStyleSelect = document.getElementById('poemStyle');
    const poemThemeInput = document.getElementById('poemTheme');
    const styleError = document.getElementById('styleError');
    const themeError = document.getElementById('themeError');

    // 为风格选择添加验证
    poemStyleSelect.addEventListener('change', function () {
        if (!this.value) {
            styleError.textContent = '请选择诗词风格';
            styleError.style.display = 'block';
        } else {
            styleError.style.display = 'none';
        }
    });

    // 为主题输入添加验证
    poemThemeInput.addEventListener('input', function () {
        if (!this.value.trim()) {
            themeError.textContent = '请输入主题意境';
            themeError.style.display = 'block';
        } else if (this.value.length > 20) {
            themeError.textContent = '主题意境不能超过20个字';
            themeError.style.display = 'block';
        } else {
            themeError.style.display = 'none';
        }
    });

    // 提交诗词处理
    submitBtn.addEventListener('click', function () {
        const title = poemTitleInput.value.trim();
        const content = poemContentInput.value.trim();

        const style = poemStyleSelect.value;
        const theme = poemThemeInput.value.trim();

        // 重置错误提示
        styleError.style.display = 'none';
        themeError.style.display = 'none';


        // 验证输入
        let isValid = true;

        if (!style) {
            styleError.textContent = '请选择诗词风格';
            styleError.style.display = 'block';
            isValid = false;
        }

        if (!theme) {
            themeError.textContent = '请输入主题意境';
            themeError.style.display = 'block';
            isValid = false;
        } else if (theme.length > 20) {
            themeError.textContent = '主题意境不能超过20个字';
            themeError.style.display = 'block';
            isValid = false;
        }

        if (!isValid) {
            // 自动滚动到第一个错误处
            const firstError = document.querySelector('.error-message[style*="display: block"], .error-hint[style*="display: block"]');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            return;
        }


        // 清除错误信息
        errorMessage.style.display = 'none';

        // 显示加载状态
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 提交中...';
        submitBtn.disabled = true;

        // 发送数据到服务器
        submitPoemToServer(title, content, style, theme);
    });

    // 历史记录容器
    const historyContainer = document.createElement('div');
    historyContainer.id = 'historyContainer';
    historyContainer.className = 'history-container';

    // 历史记录按钮
    const historyBtn = document.createElement('button');
    historyBtn.id = 'historyBtn';
    historyBtn.className = 'history-btn';
    historyBtn.innerHTML = '<i class="fas fa-history"></i> 历史记录';

    // 将历史记录按钮添加到输入区域
    const poemInput = document.querySelector('.poem-input');
    poemInput.appendChild(historyBtn);

    // 历史记录弹出层
    const historyPopup = document.createElement('div');
    historyPopup.id = 'historyPopup';
    historyPopup.className = 'history-popup';
    historyPopup.innerHTML = `
        <div class="popup-header">
            <h3>历史记录</h3>
            <button class="close-popup"><i class="fas fa-times"></i></button>
        </div>
        <div class="history-list" id="historyList"></div>
    `;

    document.body.appendChild(historyPopup);

    // 显示/隐藏历史记录
    historyBtn.addEventListener('click', function () {
        historyPopup.style.display = 'block';
        loadHistory();
    });

    historyPopup.querySelector('.close-popup').addEventListener('click', function () {
        historyPopup.style.display = 'none';
    });

    // 历史记录管理功能
    const HISTORY_KEY = 'poem_history';

    function saveToHistory(title, content, style, theme) {
        const history = JSON.parse(localStorage.getItem(HISTORY_KEY)) || [];
        const newEntry = {
            id: Date.now(),
            title: title,
            content: content,
            style: style,
            theme: theme,
            timestamp: new Date().toISOString()
        };

        // 保留最多10条记录
        const updatedHistory = [newEntry, ...history.slice(0, 9)];
        localStorage.setItem(HISTORY_KEY, JSON.stringify(updatedHistory));
    }

    function loadHistory() {
        const historyList = document.getElementById('historyList');
        historyList.innerHTML = '';

        const history = JSON.parse(localStorage.getItem(HISTORY_KEY)) || [];

        if (history.length === 0) {
            historyList.innerHTML = '<p class="empty-history">暂无历史记录</p>';
            return;
        }

        history.forEach(entry => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            historyItem.dataset.id = entry.id;

            // 格式化日期
            const date = new Date(entry.timestamp);
            const dateStr = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;

            historyItem.innerHTML = `
                <div class="history-header">
                    <h4>${entry.title}</h4>
                    <span>${dateStr}</span>
                </div>
                <div class="history-content">${entry.content.substring(0, 50)}${entry.content.length > 50 ? '...' : ''}</div>
                <div class="history-actions">
                    <button class="use-history"><i class="fas fa-check"></i> 使用</button>
                    <button class="delete-history"><i class="fas fa-trash"></i></button>
                </div>
            `;

            historyItem.querySelector('.use-history').addEventListener('click', () => {
                useHistory(entry);
                historyPopup.style.display = 'none';
            });

            historyItem.querySelector('.delete-history').addEventListener('click', () => {
                deleteHistory(entry.id);
                historyItem.remove();
                if (document.querySelectorAll('.history-item').length === 0) {
                    historyList.innerHTML = '<p class="empty-history">暂无历史记录</p>';
                }
            });

            historyList.appendChild(historyItem);
        });
    }

    function useHistory(entry) {
        poemTitleInput.value = entry.title;
        poemContentInput.value = entry.content;
        poemStyleSelect.value = entry.style || '';
        poemThemeInput.value = entry.theme || '';
        // 验证并显示历史记录中的风格和主题
        if (poemStyleSelect.value) {
            poemStyleSelect.dispatchEvent(new Event('change'));
        }
        if (poemThemeInput.value) {
            poemThemeInput.dispatchEvent(new Event('input'));
        }
        // 自动提交
        submitBtn.click();
    }

    function deleteHistory(id) {
        const history = JSON.parse(localStorage.getItem(HISTORY_KEY)) || [];
        const updatedHistory = history.filter(entry => entry.id !== id);
        localStorage.setItem(HISTORY_KEY, JSON.stringify(updatedHistory));
    }

    // 发送诗词到服务器
    function submitPoemToServer(title, content, style, theme) {
        fetch('/api/submit-poem', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: title,
                content: content,
                style: style,   // 新增
                theme: theme    // 新增
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 成功后更新UI
                    console.log(data);
                    // 保存到历史记录
                    saveToHistory(title, content);
                    // 假设提交成功，然后调用润色功能
                    polishPoem(title, content);
                    // 假设提交成功，然后调用评分功能
                    fetchScoring(title, content);
                    // 获取诗歌推荐
                    fetchRecommendations(content);

                    // 切换到润色标签页
                    document.querySelector('[data-target="editing"]').click();
                } else {
                    console.error('提交失败');
                }
            })
            .catch(error => {
                console.error('提交错误:', error);
            })
            .finally(() => {
                // 恢复按钮状态
                submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> 提交诗词';
                submitBtn.disabled = false;
            });
    }
    // 获取润色相关元素
    const regeneratePolishBtn = document.getElementById('regeneratePolish');
    const polishStatus = document.getElementById('polishStatus');
    const polishedVersion1 = document.getElementById('polishedVersion1');
    const polishedVersion2 = document.getElementById('polishedVersion2');
    const version1Title = document.getElementById('version1Title');
    const version2Title = document.getElementById('version2Title');

    // 润色功能
    function polishPoem(title, content, style, theme) {
        // 显示加载状态
        polishStatus.style.display = 'block';
        regeneratePolishBtn.disabled = true;

        // 清空之前的润色结果
        polishedVersion1.textContent = '';
        polishedVersion2.textContent = '';
        version1Title.textContent = title;
        version2Title.textContent = title;

        // 模拟API调用（实际开发中替换为真实API）
        // 这里假设API返回两个润色版本，实际根据后端接口调整
        fetch('/api/polish-poem', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: title,
                content: content,
                style: style,   // 新增
                theme: theme    // 新增
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 显示润色结果
                    polishedVersion1.textContent = data.polishedContent1 || "润色版本一生成失败";
                    polishedVersion2.textContent = data.polishedContent2 || "润色版本二生成失败";
                } else {
                    polishedVersion1.textContent = "润色失败，请重试";
                    polishedVersion2.textContent = "润色失败，请重试";
                }
            })
            .catch(error => {
                console.error('润色错误:', error);
                polishedVersion1.textContent = "网络错误，请重试";
                polishedVersion2.textContent = "网络错误，请重试";
            })
            .finally(() => {
                // 隐藏加载状态
                polishStatus.style.display = 'none';
                regeneratePolishBtn.disabled = false;
            });
    }

    // 重新润色按钮
    regeneratePolishBtn.addEventListener('click', function () {
        const title = poemTitleInput.value.trim();
        const content = poemContentInput.value.trim();
        const style = document.getElementById('poemStyle').value;
        const theme = document.getElementById('poemTheme').value.trim();


        if (title && content) {
            polishPoem(title, content, style, theme);
        } else {
            alert("请先输入诗词内容");
        }
    });
    // chinesePage.js
    // 获取智能评分数据
    function fetchScoring(title, content) {
        fetch('/api/scoring', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, content })
        })
            .then(response => response.json())
            .then(data => {
                // 更新综合得分
                document.querySelector('.score-number').textContent = data.overall_score;

                // 清空评分容器
                const ratingList = document.querySelector('.rating-grid');
                ratingList.innerHTML = '';

                // 创建紧凑的网格布局
                const ratingGrid = document.createElement('div');
                ratingGrid.className = 'rating-grid compact-grid';
                ratingList.appendChild(ratingGrid);

                // 创建所有评分项
                data.ratings.forEach((rating) => {
                    const ratingItem = document.createElement('div');
                    ratingItem.className = 'rating-item compact hover-effect';

                    ratingItem.innerHTML = `
                <div class="rating-title">
                    <i class="fas fa-star"></i>
                    <span>${rating.title}</span>
                    <span class="rating-score">${rating.score}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-value" style="width: ${rating.progress}%"></div>
                </div>
            `;

                    ratingGrid.appendChild(ratingItem);
                });
            })
            .catch(error => console.error('Error fetching scoring data:', error));
    }
    // 获取用户诗词内容并请求推荐
    function fetchRecommendations(content) {
        fetch('/api/recommend-poems', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: content })
        })
            .then(response => response.json())
            .then(data => {
                // 获取读写共生模块容器
                const poemList = document.querySelector('.poem-list');
                poemList.innerHTML = '';

                // 处理推荐结果
                const poems = data.recommendedPoems || [];

                // 如果没有推荐结果或推荐失败，使用默认数据
                if (poems.length === 0) {
                    poems.push({
                        title: "《静夜思》",
                        poet: "李白",
                        content: "床前明月光，疑是地上霜。\n举头望明月，低头思故乡。",
                        summary: "一首表达思乡之情的经典五言绝句"
                    });
                }

                // 创建推荐诗歌项目
                poems.forEach(poem => {
                    const poemItem = document.createElement('div');
                    poemItem.className = 'poem-item hover-effect';

                    // 替换换行符为HTML换行标签
                    const formattedContent = poem.content.replace(/\n/g, '<br>');

                    poemItem.innerHTML = `
                <div class="poem-header">
                    <h4>${poem.title}</h4>
                    <span class="poet">${poem.poet}</span>
                </div>
                <div class="poem-content">
                    ${formattedContent}
                </div>
                <div class="poem-summary">
                    <p>${poem.summary}</p>
                </div>
            `;

                    poemList.appendChild(poemItem);
                });
            })
            .catch(error => {
                console.error('获取推荐失败:', error);
                // 错误处理
                const poemList = document.querySelector('.poem-list');
                poemList.innerHTML = '<p class="error">推荐加载失败，请稍后再试</p>';
            });
    }

});
