/* 以图赋诗 */
document.addEventListener('DOMContentLoaded', function () {
    const generateBtn = document.getElementById('generateBtn');
    const imageUpload = document.getElementById('imageUpload');
    const uploadArea = document.getElementById('uploadArea');
    const imagePreview = document.getElementById('imagePreview');
    const poemResult = document.getElementById('poemResult');
    let uploadedImage = null;

    // 文件上传事件
    imageUpload.addEventListener('change', function (e) {
        const file = e.target.files[0];
        if (file) {
            // 验证文件类型
            if (!file.type.match('image.*')) {
                alert('请上传图片文件 (JPG, PNG等)');
                return;
            }
            // 预览图片
            const reader = new FileReader();
            reader.onload = function (e) {
                uploadedImage = file;
                // 创建预览图片元素
                imagePreview.innerHTML = `
                <img src="${e.target.result}" 
                     alt="图片预览" 
                     style="max-width: 100%; max-height: 300px; border-radius: 8px;">
            `;
                uploadArea.classList.add('has-image');
            };
            reader.readAsDataURL(file);
            const label = document.getElementsByClassName(
                'upload-btn'
            );
            label[0].style.display = 'none'; // 隐藏上传按钮
        }
    });

    // 生成按钮事件
    generateBtn.addEventListener('click', async function () {
        if (!uploadedImage) {
            alert('请先上传图片');
            return;
        }

        // 显示加载动画
        poemResult.innerHTML = '<div class="loader"></div>';
        generateBtn.disabled = true;
        generateBtn.textContent = '生成中...';

        try {
            // 创建FormData对象
            const formData = new FormData();
            formData.append('image', uploadedImage);

            // 调用后端API
            const response = await fetch('/generate_poem', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('诗歌生成失败');
            }

            const result = await response.json();

            // 显示生成的诗歌
            poemResult.innerHTML = `
                <div class="poem-content">
                    <div class="poem-text">
                        <pre>${result.poem}</pre>
                    </div>
                </div>
                <div class="poem-actions">
                    <button id="copyBtn" class="action-btn"><i class="fas fa-copy"></i> 复制</button>
                    <button id="saveBtn" class="action-btn"><i class="fas fa-save"></i> 保存</button>
                    <button id="regenerateBtn" class="action-btn"><i class="fas fa-redo"></i> 重新生成</button>
                </div>
            `;

            // 添加复制功能
            document.getElementById('copyBtn').addEventListener('click', function () {
                navigator.clipboard.writeText(result.poem)
                    .then(() => alert('诗歌已复制到剪贴板'))
                    .catch(err => console.error('复制失败:', err));
            });

            // 添加保存功能
            document.getElementById('saveBtn').addEventListener('click', function () {
                const blob = new Blob([result.poem], { type: 'text/plain' });
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = 'AI生成诗歌.txt';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            });

            // 添加重新生成功能
            document.getElementById('regenerateBtn').addEventListener('click', function () {
                generateBtn.click();
            });

        } catch (error) {
            console.error('生成诗歌失败:', error);
            poemResult.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle" style="color: #ff6b6b; font-size: 2rem;"></i>
                    <p>生成失败: ${error.message}</p>
                    <button id="retryBtn" class="action-btn">重试</button>
                </div>
            `;
            document.getElementById('retryBtn').addEventListener('click', function () {
                generateBtn.click();
            });
        } finally {
            generateBtn.disabled = false;
            generateBtn.textContent = '开始创作';
        }
    });
});