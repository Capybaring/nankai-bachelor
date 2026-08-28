from flask import Flask, request, redirect, url_for, session
from waitress import serve  # 使用 Waitress 服务器
from blueprints.home import home_bp  # 首页蓝图
from blueprints.auth import auth_bp  # 登录注册
from blueprints.poem import poem_bp  # 诗文分析
from blueprints.paint import paint_bp  # 图文生成
from blueprints.classicalChinese import classical_chinese_bp  # 文言文
from blueprints.material import material_bp  # 素材库

app = Flask(__name__)
app.secret_key = "123456"

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(poem_bp)
app.register_blueprint(classical_chinese_bp)
app.register_blueprint(material_bp)
app.register_blueprint(paint_bp)


@app.before_request
def require_login():
    allowed = {
        "home.index",  # 蓝图首页
        "auth.login",  # 蓝图 auth 的登录页
        "auth.register",  # 蓝图 auth 的注册页
        "static",  # 静态资源
    }
    if (
        request.endpoint
        and "username" not in session
        and request.endpoint not in allowed
    ):
        return redirect(url_for("auth.login"))


# 运行
if __name__ == "__main__":
    serve(app, host="127.0.0.1", port=5000, threads=8)
