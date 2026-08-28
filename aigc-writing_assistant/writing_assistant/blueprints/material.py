from flask import render_template, request, jsonify, Blueprint
import logging
from openai import OpenAI

# ChatAnywhere OpenAI 兼容 API 配置
OPENAI_API_KEY = "sk-S75vNa5oqOZp7A1ZSiQFPYc4FgLNfaksUYFaRWFFqPtRXmUC"
OPENAI_BASE_URL = "https://api.chatanywhere.tech/v1"

# 初始化 OpenAI 客户端
client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
material_bp = Blueprint(
    "material",
    __name__,
    template_folder="templates",
    static_folder="static",
)

# 设置日志记录
logging.basicConfig(level=logging.INFO)


def generate_poetry_prompt(query):
    return f"""
你是一位熟悉中国古诗词的AI助手。
请根据用户输入的关键词“{query}”，提供一个相关的古诗词内容或分析说明。
1、包括：作者简介（如有），诗句出处，以及其在语文作文或文化理解上的应用价值。
2、推荐3首不同的诗词，然后进行分析
3、分析总字数不少于1500字
4、严格控制输出的格式，不要出现 '#','*'等
"""


# 路由：返回中文学习页面
@material_bp.route("/material")
def material():
    return render_template("material.html")


@material_bp.route("/search", methods=["POST"])
def search():
    try:
        # 获取前端发送的JSON数据
        data = request.get_json()
        query = data.get("query", "").strip()

        if not query:
            return jsonify({"result": "请输入有效的关键词。"})

        prompt = generate_poetry_prompt(query)

        logging.info(f"请求查询: {query}")  # 打印查询内容到终端

        # 调用 ChatAnywhere 的 Chat API（兼容 OpenAI）
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # 或 gpt-4 等 ChatAnywhere 支持的模型
            messages=[
                {"role": "system", "content": "你是一个专业的古诗词讲解助手"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=4000,
        )

        # 打印完整的响应对象（调试用）
        logging.info(f"API 返回响应: {response}")

        # 提取并返回结果
        answer = response.choices[0].message.content.strip().replace("*", "")
        logging.info(f"返回结果: {answer}")  # 打印结果到终端

        return jsonify({"result": answer})

    except Exception as e:
        logging.error(f"查询过程中发生错误: {str(e)}")
        return jsonify({"result": f"查询出错: {str(e)}"})
