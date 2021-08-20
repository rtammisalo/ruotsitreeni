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
        password_again = request.form["inputPasswordAgain"]

        password_mismatch_error = ""
        if password != password_again:
            password_mismatch_error = "Annetut salasanat eivät täsmää."

        username_error = users.validate_username(username)
        password_error = users.validate_password(password)

        if username_error or password_error or password_mismatch_error:
            error = helpers.Error()
            error.add("inputUsername", username_error)
            error.add("inputPassword", password_error)
            error.add("inputPasswordAgain", password_mismatch_error)
            return helpers.render_create_user(error)

        users.create(username, password)
    except users.CreateUserError as err:
        return helpers.render_create_user(err)

    return redirect("/")


@ app.route("/logout")
def logout_user():
    if users.get_logged_user_id():
        users.logout()

    return redirect("/")
