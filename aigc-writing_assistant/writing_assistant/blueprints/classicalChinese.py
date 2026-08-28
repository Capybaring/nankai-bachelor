from flask import (
    Blueprint,
    render_template,
    jsonify,
    request,
)
import json
from openai import OpenAI

# 火山引擎API配置
VOLCANO_API_KEY = "ccb4f407-09f5-4d2e-9034-aa89d93abb21"
VOLCANO_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MODEL_NAME = "doubao-1-5-thinking-pro-250415"

# 初始化OpenAI客户端
client = OpenAI(api_key=VOLCANO_API_KEY, base_url=VOLCANO_BASE_URL)

# 创建蓝图
classical_chinese_bp = Blueprint(
    "classical_chinese",
    __name__,
    template_folder="templates",
    static_folder="static",
)


# 页面：文言文分析主页面
@classical_chinese_bp.route("/classicalChinese")
def classicalChinese():
    return render_template("classicalChinese.html")


# 接口：逐句翻译
@classical_chinese_bp.route("/api/translate", methods=["POST"])
def translate():
    try:
        data = request.get_json()
        content = data.get("content")

        if not content:
            return jsonify({"success": False, "message": "内容不能为空"}), 400

        system_prompt = """
你是一位精通古汉语和现代汉语对照翻译的语言专家。

请将用户提供的一段文言文逐句翻译为通顺、准确的现代汉语。要求：

1. 保持每一句的语义完整性；
2. 用现代书面语表达，不使用口语或文言色彩；
3. 翻译结果按原文顺序排列，逐句对应；
4. 返回内容为 JSON 格式，例如：

{
    "translations": [
        {
            "original": "昔者庄周梦为胡蝶。",
            "translation": "从前庄周梦见自己变成了一只蝴蝶。"
        },
        {
            "original": "栩栩然胡蝶也，自喻适志与！",
            "translation": "栩栩如生地像只蝴蝶，自以为非常自由快乐！"
        }
    ]
}
"""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content},
            ],
            temperature=0.3,
            max_tokens=2000,
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)
        all_translation = " ".join(
            [item["translation"] for item in result["translations"]]
        )
        return jsonify({"success": True, "translation": all_translation})

    except Exception as e:
        if "maximum context length" in str(e):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "token_limit_exceeded",
                        "message": "文本内容过长，请减少输入内容后重试",
                    }
                ),
                400,
            )
        raise e
    except Exception as e:
        return jsonify({"success": False, "message": f"翻译失败: {str(e)}"}), 500


# 接口：重点字词解释
@classical_chinese_bp.route("/api/explain-words", methods=["POST"])
def explain_words():
    try:
        data = request.get_json()
        content = data.get("content")

        if not content:
            return jsonify({"success": False, "message": "内容不能为空"}), 400

        system_prompt = """
你是一位擅长文言文语言分析的专家，请对用户提供的文言文内容进行语言现象分析。请按如下四类进行分类，并返回结构化 JSON 数据：

1. 通假字：列出通假字及其本字，并解释其含义；
2. 古今异义词：列出词语，给出古义、今义，并解释差异；
3. 词类活用：指出活用词，说明活用前后词性及句中功能；
4. 特殊句式：列出判断句、被动句、省略句等典型句式并解释。

请严格按照以下 JSON 格式返回：

{
  "phonetic_substitutions": [
    {
      "word": "乡",
      "original": "向",
      "explanation": ""乡"是"向"的通假字，表示方向。"
    }
  ],
  "semantic_shifts": [
    {
      "word": "走",
      "ancient_meaning": "奔跑",
      "modern_meaning": "步行",
      "explanation": ""走"在古代表示奔跑，现代表示步行，含义发生了变化。"
    }
  ],
  "functional_shifts": [
    {
      "word": "使",
      "original_pos": "动词",
      "shifted_pos": "名词",
      "explanation": ""使"在句中由动词"派遣"活用为名词，表示"使者"。"
    }
  ],
  "special_sentence_patterns": [
    {
      "type": "判断句",
      "example": "此人者，吾师也。",
      "explanation": "使用"者……也"结构，表明判断关系。"
    }
  ]
}
"""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content},
            ],
            temperature=0.3,
            max_tokens=2000,
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)
        return jsonify({"success": True, "result": result})

    except Exception as e:
        error_message = str(e)
        if "maximum context length" in error_message:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "token_limit_exceeded",
                        "message": "文本内容过长，请减少输入内容后重试",
                    }
                ),
                400,
            )
        return jsonify({"success": False, "message": f"解释失败: {error_message}"}), 500


@classical_chinese_bp.route("/api/analyze-theme", methods=["POST"])
def analyze_theme():
    try:
        data = request.get_json()
        content = data.get("content")

        if not content:
            return jsonify({"success": False, "message": "内容不能为空"}), 400

        system_prompt = """
你是一位文言文专家和语文教学顾问，请从文学分析的角度对用户提供的文言文材料进行主旨分析，包含以下四个方面：

1. 中心思想：作者想要表达的核心观点或情感；
2. 艺术特色：语言风格、结构布局、修辞特色等方面；
3. 历史背景：创作背景与社会文化环境的关系。

请按照如下 JSON 格式返回：

{
    "analysis": {
        "main_theme": "本文通过庄周梦蝶的故事，表达了对人生与真实的哲思。",
        "artistic_features": "语言简洁含蓄，结构精巧，寓理于事。",
        "historical_background": "出自《庄子》，战国时期诸子百家争鸣背景下的哲学思考。"
    }
}
"""

        print(f"正在分析内容: {content[:100]}...")  # 打印输入内容的前100个字符

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content},
            ],
            temperature=0.3,
            max_tokens=2000,
            response_format={"type": "json_object"},
        )

        print(f"API响应: {response.choices[0].message.content}")  # 打印API响应

        result = json.loads(response.choices[0].message.content)

        # 处理可能的列表格式响应
        if isinstance(result, list) and len(result) > 0:
            result = result[0]  # 取第一个元素

        if "analysis" not in result:
            print(f"API返回格式错误: {result}")
            return jsonify({"success": False, "message": "API返回格式不正确"}), 500

        return jsonify({"success": True, "analysis": result["analysis"]})

    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {str(e)}")
        return jsonify({"success": False, "message": "返回数据格式错误"}), 500
    except Exception as e:
        error_message = str(e)
        print(f"分析过程中出现错误: {error_message}")

        if "maximum context length" in error_message:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "token_limit_exceeded",
                        "message": "文本内容过长，请减少输入内容后重试",
                    }
                ),
                400,
            )

        return jsonify({"success": False, "message": f"分析失败: {error_message}"}), 500
