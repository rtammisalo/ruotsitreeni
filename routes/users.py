from flask import redirect, request
from flask_init import app
from routes import helpers
import users


@ app.route("/login", methods=["POST"])
def login():
    if users.get_logged_user_id():
        return redirect("/")

    username = request.form["inputUsername"]
    password = request.form["inputPassword"]

    try:
        users.login(username, password)
    except users.LoginUserError as err:
        return helpers.render_login(error=err)

    return redirect("/")


@ app.route("/create_user", methods=["POST", "GET"])
def create_user():
    if users.get_logged_user_id():
        return redirect("/")

    if request.method == "GET":
        return helpers.render_create_user()

    try:
        username = request.form["inputUsername"]
        password = request.form["inputPassword"]

        users.create(username, password)
    except users.CreateUserError as err:
        return helpers.render_create_user(err)

    return redirect("/")


@ app.route("/logout")
def logout_user():
    if users.get_logged_user_id():
        users.logout()

    return redirect("/")
