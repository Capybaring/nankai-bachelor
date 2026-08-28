from flask import (
    Blueprint,
    render_template,
    request,
    session,
    redirect,
    url_for,
)
from werkzeug.security import generate_password_hash, check_password_hash
import os

# 获取当前文件的绝对路径
current_file = os.path.abspath(__file__)
# 获取父目录（上一级）
current_dir = os.path.dirname(current_file)
# 再获取父目录的父目录（上两级）
parent_dir = os.path.dirname(current_dir)
# 拼接出数据库文件的完整路径
DB_PATH = os.path.join(parent_dir, "db", "users.db")
auth_bp = Blueprint(
    "auth",
    __name__,
    template_folder="templates",
    static_folder="static",
)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        import sqlite3

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, password FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if not user:
            error = "用户名不存在"
        elif not check_password_hash(user[1], password):
            error = "密码错误"
        else:
            session["user_id"] = user[0]
            session["username"] = username
            return redirect(url_for("home.index"))
    return render_template("login.html", error=error)


# 注册
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    error = None
    success = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")
        if not username or not password or not password2:
            error = "所有字段均为必填"
        elif password != password2:
            error = "两次输入的密码不一致"
        else:
            import sqlite3

            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id FROM users WHERE username=?", (username,))
            if c.fetchone():
                error = "用户名已存在"
            else:
                hashed = generate_password_hash(password)
                c.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hashed),
                )
                conn.commit()
                success = "注册成功，请登录"
            conn.close()
    return render_template("register.html", error=error, success=success)


# 注销
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home.index"))
