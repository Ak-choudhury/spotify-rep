from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, current_user
from app.services.auth_service import AuthService
from app.models import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("library.index"))

    error = None

    if request.method == "POST":
        user = AuthService.verify_credentials(
            request.form["username"],
            request.form["password"]
        )

        if user:
            login_user(user)
            return redirect(url_for("library.index"))

        error = "Invalid username or password"

    return render_template("login.html", error=error)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        if User.query.filter_by(username=request.form["username"]).first():
            error = "Username already exists"
        else:
            user = AuthService.create_user(
                request.form["username"],
                request.form["password"]
            )
            login_user(user)
            return redirect(url_for("library.index"))

    return render_template("register.html", error=error)


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
