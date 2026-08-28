from flask import Blueprint, render_template

home_bp = Blueprint(
    "home", __name__, template_folder="templates", static_folder="static"
)


# 首页
@home_bp.route("/")
def index():
    return render_template("index.html")
