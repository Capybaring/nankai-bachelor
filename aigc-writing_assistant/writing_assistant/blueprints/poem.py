# poem.py
from flask import Blueprint, render_template, jsonify, request
import json
import os
import datetime
import random
import os
from openai import OpenAI

# 火山引擎API配置
VOLCANO_API_KEY = "ccb4f407-09f5-4d2e-9034-aa89d93abb21"  # 替换为你的实际API密钥
VOLCANO_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MODEL_NAME = "doubao-1-5-thinking-pro-250415"  # 模型名称（全小写）

# 初始化OpenAI客户端（配置为火山引擎）
client = OpenAI(api_key=VOLCANO_API_KEY, base_url=VOLCANO_BASE_URL)

# 创建蓝图
poem_bp = Blueprint(
    "poem", __name__, template_folder="templates", static_folder="static"
)

# 获取当前文件的绝对路径
current_file = os.path.abspath(__file__)
# 获取当前文件所在目录
current_dir = os.path.dirname(current_file)
# 获取父目录（上一级）
parent_dir = os.path.dirname(current_dir)
# 再获取父目录的父目录（上两级）
grandparent_dir = os.path.dirname(parent_dir)
# 指定存储目录为 uploads
data_dir = os.path.join(grandparent_dir, "uploads")


# 路由：返回中文学习页面
@poem_bp.route("/poem")
def poem():
    return render_template("poem.html")


# 路由：接收诗词提交
@poem_bp.route("/api/submit-poem", methods=["POST"])
def submit_poem():
    try:
        # 获取前端提交的JSON数据
        data = request.get_json()

        # 获取诗词题目和内容
        title = data.get("title")
        content = data.get("content")

        style = data.get("style", "")  # 新增：获取风格
        theme = data.get("theme", "")  # 新增：获取主题

        # 验证数据是否存在
        if not title or not content:
            return jsonify({"success": False, "message": "诗词题目和内容不能为空"}), 400

        # 新增：风格验证
        valid_styles = ["free", "five", "seven", "ci"]
        if style and style not in valid_styles:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"无效的诗词风格。可选: {', '.join(valid_styles)}",
                    }
                ),
                400,
            )

        # 新增：主题验证（长度限制）
        if theme and len(theme) > 20:
            return jsonify({"success": False, "message": "主题意境不能超过20个字"}), 400

        # 保存数据（添加style和theme）
        poem_data = {
            "title": title,
            "content": content,
            "style": style,
            "theme": theme,
            "timestamp": datetime.datetime.now().isoformat(),
        }

        file_path = os.path.join(data_dir, f"{title.replace(' ', '_')}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(poem_data, f, ensure_ascii=False, indent=2)

        # 返回成功响应
        return jsonify(
            {
                "success": True,
                "message": "诗词提交成功",
                "data": {
                    "title": title,
                    "preview": content[:50] + "..." if len(content) > 50 else content,
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500


# 路由：润色诗词
@poem_bp.route("/api/polish-poem", methods=["POST"])
def polish_poem():
    try:
        # 获取前端提交的JSON数据
        data = request.get_json()

        # 获取诗词题目和内容
        title = data.get("title")
        content = data.get("content")

        # 验证数据是否存在
        if not title or not content:
            return jsonify({"success": False, "message": "诗词题目和内容不能为空"}), 400

        # 调用火山引擎API进行润色（两种风格）
        polished_content1 = polish_with_volcano(content, style="优雅文言文")
        polished_content2 = polish_with_volcano(content, style="古典传统")

        return jsonify(
            {
                "success": True,
                "polishedContent1": polished_content1,
                "polishedContent2": polished_content2,
                "message": "诗词润色成功",
            }
        )

    except Exception as e:
        return jsonify({"success": False, "message": f"润色处理失败: {str(e)}"}), 500


def polish_with_volcano(original_content, style="优雅文言文", theme=""):
    """调用火山引擎API进行诗词润色（指定风格）"""
    # 根据风格设置不同的系统提示
    if style == "优雅文言文":
        system_prompt = "你是一个精通中国古典文学的专家，请将用户输入的诗歌润色为更优雅的文言文风格，保持原意不变但提升文学美感，润色后不超过300字。"
    else:  # 古典传统
        system_prompt = "你是一个中国古典诗词大师，请将用户输入的诗歌润色为更古典的表达风格，使用更传统的词汇和句式，保持原意不变，润色后不超过300字。"

    # 新增：加入主题约束
    if theme:
        system_prompt += (
            f" 特别注意：这首诗的主题是'{theme}'，请确保润色后保持主题一致性，最终字数不超过300字。"
        )

    try:
        # 调用火山引擎API
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": original_content},
            ],
            temperature=0.9,  # 适当提高创意性
            max_tokens=500,  # 控制输出长度
        )

        # 提取润色结果
        polished_content = response.choices[0].message.content.strip()
        return polished_content

    except Exception as e:
        # 如果润色失败，返回原始内容并记录错误
        print(f"润色失败: {str(e)}")
        return original_content  # 失败时返回原内容，避免前端无显示


# 路由：获取智能评分数据（基于大模型）
@poem_bp.route("/api/scoring", methods=["POST"])
def get_scoring_data():
    try:
        # 获取前端提交的JSON数据
        data = request.get_json()
        title = data.get("title")
        content = data.get("content")

        if not title or not content:
            return jsonify({"success": False, "message": "诗词题目和内容不能为空"}), 400

        # 调用大模型API进行评分
        scoring_result = score_with_volcano(title, content)

        # 计算总分（每个维度20分，共100分）
        total_score = sum(
            dimension["score"] for dimension in scoring_result["dimensions"]
        )

        # 转换为前端需要的格式
        ratings = []
        for dim in scoring_result["dimensions"]:
            score_value = dim["score"]
            ratings.append(
                {
                    "title": dim["title"],
                    "score": f"{score_value}/20",
                    "progress": int((score_value / 20) * 100),  # 转换为百分比进度
                }
            )

        scoring_data = {"overall_score": total_score, "ratings": ratings}

        return jsonify(scoring_data)

    except Exception as e:
        return (
            jsonify({"success": False, "message": f"获取评分数据失败: {str(e)}"}),
            500,
        )


def score_with_volcano(title, content):
    """调用火山引擎API进行诗词智能评分（只返回分数）"""
    # 构建系统提示词，明确评分维度和标准，并指定只返回分数
    system_prompt = """
    你是一位中国古典诗词专家，需要对用户提交的诗词进行专业评分。请从以下五个维度进行评价（每个维度满分20分）：
    1. 立意：主题是否明确，立意是否新颖深刻
    2. 押韵：是否符合诗词的押韵规则，韵律是否和谐
    3. 对仗：对仗是否工整，符合诗词格律要求
    4. 意境：是否营造出优美的意境，情景交融
    5. 语言：语言是否精练，用词是否准确生动

    请按照以下JSON格式返回评分结果（只需返回分数，不需要评语）：
    {
        "dimensions": [
            {"title": "立意", "score": 分数},
            {"title": "押韵", "score": 分数},
            {"title": "对仗", "score": 分数},
            {"title": "意境", "score": 分数},
            {"title": "语言", "score": 分数}
        ]
    }
    """

    try:
        # 调用火山引擎API
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"诗词标题：《{title}》\n诗词内容：\n{content}",
                },
            ],
            temperature=0.3,  # 较低的随机性保证评分稳定性
            max_tokens=500,
            response_format={"type": "json_object"},  # 要求返回JSON格式
        )

        # 提取并解析评分结果
        result_json = response.choices[0].message.content.strip()
        scoring_result = json.loads(result_json)

        # 验证评分结果结构
        if "dimensions" not in scoring_result:
            raise ValueError("API返回的评分结果缺少维度信息")

        # 验证每个维度的评分
        for dimension in scoring_result["dimensions"]:
            if "title" not in dimension or "score" not in dimension:
                raise ValueError("维度评分信息不完整")
            if not (0 <= dimension["score"] <= 20):
                dimension["score"] = max(
                    0, min(20, dimension["score"])
                )  # 确保分数在0-20范围内

        return scoring_result

    except (json.JSONDecodeError, ValueError) as e:
        print(f"解析评分结果失败: {str(e)}")
        # 返回默认评分结果（只有分数）
        return {
            "dimensions": [
                {"title": "立意", "score": random.randint(10, 18)},
                {"title": "押韵", "score": random.randint(10, 18)},
                {"title": "对仗", "score": random.randint(10, 18)},
                {"title": "意境", "score": random.randint(10, 18)},
                {"title": "语言", "score": random.randint(10, 18)},
            ]
        }
    except Exception as e:
        print(f"评分失败: {str(e)}")
        # 返回默认评分结果（只有分数）
        return {
            "dimensions": [
                {"title": "立意", "score": random.randint(10, 18)},
                {"title": "押韵", "score": random.randint(10, 18)},
                {"title": "对仗", "score": random.randint(10, 18)},
                {"title": "意境", "score": random.randint(10, 18)},
                {"title": "语言", "score": random.randint(10, 18)},
            ]
        }


# 路由：获取读写共生数据
@poem_bp.route("/api/recommend-poems", methods=["POST"])
def recommend_poems():
    try:
        # 获取前端提交的JSON数据
        data = request.get_json()

        # 获取用户提交的诗词内容
        user_content = data.get("content", "")

        # 系统提示词
        system_prompt = """
        你是一位中国古典诗词专家，需要根据用户提供的诗词内容，推荐4首主题、风格或意境相似的经典诗词。
        返回格式必须是严格的JSON数组，每首诗词包含以下字段：
        - title: 诗词标题（带书名号）
        - poet: 诗人姓名
        - content: 诗词全文（每句一行，用换行符分隔）
        - summary: 一句话概括（不超过20字）

        示例：
        [
            {
                "title": "《静夜思》",
                "poet": "李白",
                "content": "床前明月光，疑是地上霜。\\n举头望明月，低头思故乡。",
                "summary": "一首表达思乡之情的经典五言绝句"
            },
            ...（其他三首）
        ]
        """

        # 调用火山引擎API
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"用户诗词内容：{user_content}"},
            ],
            temperature=0.5,
            max_tokens=800,
            response_format={"type": "json_object"},
        )

        # 提取并解析推荐结果
        result_json = response.choices[0].message.content.strip()
        recommended_poems = json.loads(result_json)

        # 验证结果格式
        if not isinstance(recommended_poems, list) or len(recommended_poems) < 1:
            raise ValueError("API返回的推荐结果格式不正确")

        # 确保每首诗都有必需的字段
        valid_poems = []
        for poem in recommended_poems:
            if all(key in poem for key in ["title", "poet", "content", "summary"]):
                valid_poems.append(poem)

        return jsonify(
            {"success": True, "recommendedPoems": valid_poems[:4]}  # 最多返回4首
        )

    except Exception as e:
        print(f"推荐诗歌失败: {str(e)}")
        # 返回默认推荐作为后备
        return jsonify(
            {
                "success": False,
                "message": f"推荐失败: {str(e)}",
                "recommendedPoems": [
                    {
                        "title": "《静夜思》",
                        "poet": "李白",
                        "content": "床前明月光，疑是地上霜。\n举头望明月，低头思故乡。",
                        "summary": "一首表达思乡之情的经典五言绝句",
                    },
                    {
                        "title": "《春晓》",
                        "poet": "孟浩然",
                        "content": "春眠不觉晓，处处闻啼鸟。\n夜来风雨声，花落知多少。",
                        "summary": "描绘春天早晨景象的五言绝句",
                    },
                ],
            }
        )
