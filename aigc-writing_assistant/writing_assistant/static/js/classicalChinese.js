// classicalChinese.js
// 显示错误信息
function showError(module, message) {
    const errorDiv = document.getElementById(module + 'Error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

// 隐藏错误信息
function hideErrors() {
    document.querySelectorAll('.error-message').forEach(error => {
        error.style.display = 'none';
    });
}

// 清除结果
function clearResults() {
    document.querySelector('.translation-list').innerHTML = '';
    document.querySelector('.words-list').innerHTML = '';
    document.querySelector('.theme-list').innerHTML = '';
}

// 切换标签页
// ... existing code ...
document.querySelectorAll('.tab-btn').forEach(button => {
    button.addEventListener('click', () => {
        // 移除所有活动状态
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

        // 添加当前活动状态
        button.classList.add('active');
        const target = button.dataset.target;
        document.getElementById(target + 'Result').classList.add('active');
    });
});

// 分析按钮点击事件
// ... existing code ...
document.getElementById('analyzeBtn').addEventListener('click', async function () {
    const content = document.getElementById('classicalText').value;
    // 显示全局loading
    document.getElementById('globalLoading').classList.add('active');
    if (!content) {
        showError('translation', '请输入文言文内容');
        document.getElementById('globalLoading').classList.remove('active');
        return;
    }

    // 清除之前的错误和结果
    hideErrors();
    clearResults();

    try {
        // 并行处理三个请求
        const [translationResponse, wordsResponse, themeResponse] = await Promise.all([
            // 翻译请求
            fetch('/api/translate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content })
            }),
            // 字词解释请求
            fetch('/api/explain-words', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content })
            }),
            // 主旨分析请求
            fetch('/api/analyze-theme', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content })
            })
        ]);

        // 处理翻译结果
        const translationData = await translationResponse.json();
        if (translationData.success) {
            handleTranslationResult(translationData);
        } else {
            showError('translation', translationData.message || '翻译失败');
        }

        // 处理字词解释结果
        const wordsData = await wordsResponse.json();
        if (wordsData.success) {
            handleWordsResult(wordsData);
        } else {
            showError('words', wordsData.message || '字词解释失败');
        }

        // 处理主旨分析结果
        const themeData = await themeResponse.json();
        if (themeData.success) {
            handleThemeResult(themeData);
        } else {
            showError('theme', themeData.message || '主旨分析失败');
        }

    } catch (error) {
        console.error('分析失败:', error);
        showError('translation', '分析过程中出现错误，请稍后重试');
    } finally {
        // 隐藏全局loading
        document.getElementById('globalLoading').classList.remove('active');
    }
});

// 处理翻译结果
function handleTranslationResult(data) {
    const translationList = document.querySelector('.translation-list');
    if (data.translation) {
        translationList.innerHTML = `
            <div class="translation-item">
                <div class="translation">${data.translation}</div>
            </div>
        `;
    } else {
        translationList.innerHTML = '<div class="text-center">暂无翻译结果</div>';
    }
}

// 处理字词解释结果
function handleWordsResult(result) {
    const wordsList = document.querySelector('.words-list');
    let html = '';

    // 检查是否有result字段
    const data = result.result || result;

    if (data.phonetic_substitutions && data.phonetic_substitutions.length > 0) {
        html += `
            <div class="words-section">
                <h5>通假字</h5>
                ${data.phonetic_substitutions.map(item => `
                    <div class="word-item">
                        <strong>${item.word}</strong> 通 <strong>${item.original}</strong>
                        <div>${item.explanation}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    if (data.semantic_shifts && data.semantic_shifts.length > 0) {
        html += `
            <div class="words-section">
                <h5>古今异义词</h5>
                ${data.semantic_shifts.map(item => `
                    <div class="word-item">
                        <strong>${item.word}</strong>
                        <div>古义：${item.ancient_meaning}</div>
                        <div>今义：${item.modern_meaning}</div>
                        <div>${item.explanation}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    if (data.functional_shifts && data.functional_shifts.length > 0) {
        html += `
            <div class="words-section">
                <h5>词类活用</h5>
                ${data.functional_shifts.map(item => `
                    <div class="word-item">
                        <strong>${item.word}</strong>
                        <div>原词性：${item.original_pos}</div>
                        <div>活用为：${item.shifted_pos}</div>
                        <div>${item.explanation}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    if (data.special_sentence_patterns && data.special_sentence_patterns.length > 0) {
        html += `
            <div class="words-section">
                <h5>特殊句式</h5>
                ${data.special_sentence_patterns.map(item => `
                    <div class="word-item">
                        <strong>${item.type}</strong>
                        <div>例句：${item.example}</div>
                        <div>${item.explanation}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    wordsList.innerHTML = html || '<div class="text-center">暂无字词解释</div>';
}

// 处理主旨分析结果
function handleThemeResult(result) {
    const themeList = document.querySelector('.theme-list');
    const data = result.analysis || result;

    if (data && (data.main_theme || data.artistic_features || data.historical_background)) {
        themeList.innerHTML = `
            <div class="theme-section">
                <h5>中心思想</h5>
                <div class="theme-content">${data.main_theme || '暂无内容'}</div>
            </div>
            <div class="theme-section">
                <h5>艺术特色</h5>
                <div class="theme-content">${data.artistic_features || '暂无内容'}</div>
            </div>
            <div class="theme-section">
                <h5>历史背景</h5>
                <div class="theme-content">${data.historical_background || '暂无内容'}</div>
            </div>
        `;
    } else {
        themeList.innerHTML = '<div class="text-center">暂无主旨分析结果</div>';
    }
} 