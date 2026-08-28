# chinese_page.py
from flask import Blueprint, render_template, jsonify, request, current_app
from openai import OpenAI
import base64

# 火山引擎API配置
VOLCANO_API_KEY = "ccb4f407-09f5-4d2e-9034-aa89d93abb21"  # 替换为你的实际API密钥
VOLCANO_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MODEL_NAME = "doubao-1.5-vision-pro-250328"  # 模型名称（全小写）

# 初始化OpenAI客户端（配置为火山引擎）
client = OpenAI(api_key=VOLCANO_API_KEY, base_url=VOLCANO_BASE_URL)

# 创建蓝图
paint_bp = Blueprint(
    "paint", __name__, template_folder="templates", static_folder="static"
)


# 路由：返回中文学习页面
@paint_bp.route("/paint")
def paint():
    return render_template("paint.html")


# 修改：根据图片生成诗歌API
@paint_bp.route("/generate_poem", methods=["POST"])
def generate_poem():
    try:
        # 检查是否有文件上传
        if "image" not in request.files:
            return jsonify({"error": "没有上传文件"}), 400

        image_file = request.files["image"]

        # 检查文件是否为空
        if image_file.filename == "":
            return jsonify({"error": "未选择文件"}), 400

        # 检查文件类型
        if not image_file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
            return jsonify({"error": "只支持PNG、JPG、JPEG格式"}), 400

        # 读取图片内容
        image_data = image_file.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")

        # 调用火山引擎API生成诗歌
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                        {
                            "type": "text",
                            # 改进的prompt：明确格式要求
                            "text": (
                                "请根据图片内容创作一首七言律诗，要求：\n"
                                "1. 输出格式严格遵循：标题单独一行，不使用#号前缀，正文每句一行\n"
                                "2. 避免使用任何Markdown符号（如#、*等）\n"
                                "3. 不要包含任何额外说明文字\n"
                                "4. 示例格式：\n"
                                "   春园闲步\n"
                                "   小径清幽入画屏\n"
                                "   繁花绽蕊溢香馨\n"
                                "   莺啼翠柳声如织\n"
                                "   蝶舞芳丛影若星\n"
                                "   碧水含情浮藻荇\n"
                                "   青山着意耸云汀\n"
                                "   悠然漫步心欢畅\n"
                                "   胜却桃源世外经"
                            ),
                        },
                    ],
                }
            ],
            max_tokens=300,
        )

        # 获取生成的诗歌
        poem_content = response.choices[0].message.content

        return jsonify({"status": "success", "poem": poem_content})

    except Exception as e:
        current_app.logger.error(f"生成诗歌失败: {str(e)}")
        return jsonify({"status": "error", "message": f"诗歌生成失败: {str(e)}"}), 500
