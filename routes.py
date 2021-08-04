from flask import render_template, request, redirect, abort
from flask_init import app
import user

USERNAME_HELP_STRING = "Käyttäjätunnus tulee olla 3 - 12 merkkiä pitkä ja voi sisältää kirjaimia ja numeroita."
PASSWORD_HELP_STRING = "Salasanan tulee olla 6-20 merkkiä pitkä ja voi sisältää kirjaimia, erikoismerkkejä ja numeroita."


@app.route("/")
def index():
    user_id = user.get_logged_user_id()
    if user_id:
        return render_index(user_id=user_id, admin=user.is_admin())

    return render_login()


@app.route("/login", methods=["POST"])
def login():
    if user.get_logged_user_id():
        return redirect("/")

    username = request.form["inputUsername"]
    password = request.form["inputPassword"]

    try:
        user.login(username, password)
    except user.LoginUserError as err:
        return render_login(error=err)

    return redirect("/")


@app.route("/create_user", methods=["POST", "GET"])
def create_user():
    if user.get_logged_user_id():
        return redirect("/")

    if request.method == "GET":
        return render_create_user()

    try:
        username = request.form["inputUsername"]
        password = request.form["inputPassword"]

        user.create(username, password)
    except user.CreateUserError as err:
        return render_create_user(err)

    return redirect("/")


@app.route("/logout")
def logout_user():
    if user.get_logged_user_id():
        user.logout()

    return redirect("/")


def render_index(user_id=None, error=None, admin=False):
    return render_template("index.html",
                           user_id=user_id, admin=admin, error=error)


def render_login(error=None):
    return render_template("login.html", error=error)


def render_create_user(error=None):
    return render_template("create_user.html", username_help=USERNAME_HELP_STRING,
                           password_help=PASSWORD_HELP_STRING, error=error)


def abort_invalid_user_data(admin_required=False):
    try:
        csrf_token = request.form.get("csrf_token", None)

        if not csrf_token:
            raise user.UserValidationError

        user.validate_user(admin_required)

    except user.UserValidationError as err:
        abort(403)
