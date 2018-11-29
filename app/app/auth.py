import typing as T

from flask import flash, redirect, render_template, request, session

from .app import app
from .const import USERS_PATH
from .index import rt_index


def get_users() -> T.Dict[str, str]:
    ret = {}

    with USERS_PATH.open() as handle:
        for line in handle:
            line = line.rstrip()
            if not line or line.startswith("#"):
                continue

            username, password = line.split(":", 1)
            ret[username] = password

    return ret


@app.route("/login", methods=["GET", "POST"])
def rt_login() -> T.Any:
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "")
    password = request.form.get("password", "")
    users = get_users()

    if not username:
        flash("Missing user name.", "danger")
    elif not password:
        flash("Missing password.", "danger")
    elif username not in users:
        flash("Unknown user.", "danger")
    elif users[username] != password:
        flash("Invalid password.", "danger")
    else:
        # login ok
        session["user"] = username
        return redirect("/")

    return (
        render_template("login.html", username=username, password=password),
        403,
    )


@app.route("/logout")
def rt_logout() -> T.Any:
    session.pop("user")
    flash("Logged out.", "info")
    return index()
