from flask import redirect, request
from flask_init import app
from routes import helpers
import users
import answers


@app.route("/login", methods=["POST"])
def login():
    if users.get_logged_user_id():
        return redirect("/")

    username = request.form["inputUsername"]
    password = request.form["inputPassword"]

    try:
        users.login(username, password)
    except users.UserCredentialsError as err:
        return helpers.render_login(error=err)

    return redirect("/")


@app.route("/create_user", methods=["POST", "GET"])
def create_user():
    if users.get_logged_user_id():
        return redirect("/")

    if request.method == "GET":
        return helpers.render_create_user()

    try:
        username = request.form["inputUsername"]
        password = request.form["inputPassword"]
        password_again = request.form["inputPasswordAgain"]

        validator = helpers.Validator()
        validator.check_repeat_password(password, password_again)
        validator.validate_username(username)
        validator.validate_password(password)

        if not validator.error.empty():
            return helpers.render_create_user(validator.error)

        users.create(username, password)
    except users.CreateUserError as err:
        return helpers.render_create_user(err)

    return redirect("/")


@app.route("/logout")
def logout_user():
    if users.get_logged_user_id():
        users.logout()

    return redirect("/")


@app.route("/account/<int:user_id>")
def show_account(user_id, error=None, message=None):
    helpers.check_user_privileges(required_user_id=user_id)
    user = users.get_user_data_by_id(user_id)
    if user:
        stats = answers.get_user_statistics(user_id)
        kwargs = {"selected_user": user, "answers": stats,
                  "error": error, "message": message}
        return helpers.render_user_template("account.html", **kwargs)
    return helpers.abort(404)


@app.route("/account/<int:user_id>/change_password", methods=["POST"])
def change_password(user_id):
    helpers.check_user_privileges(required_user_id=user_id)
    helpers.check_csrf()

    try:
        old_password = request.form["inputOldPassword"]
        password = request.form["inputPassword"]
        password_again = request.form["inputPasswordAgain"]

        validator = helpers.Validator()
        validator.check_repeat_password(password, password_again)
        validator.check_user_password_by_id(user_id, old_password)

        if not validator.error.empty():
            return show_account(user_id, error=validator.error)

        users.change_user_password_by_id(user_id, password)
        return show_account(user_id, message="Salasana vaihdettu.")
    except users.UserCredentialsError:
        return redirect("/")


@app.route("/account/<int:user_id>/delete", methods=["GET", "POST"])
def delete_user(user_id):
    helpers.check_user_privileges(required_user_id=user_id)

    if users.is_admin() and user_id == users.get_logged_user_id():
        helpers.abort(404)

    user = users.get_user_data_by_id(user_id)
    kwargs = {"selected_user": user}

    if request.method == "GET":
        return helpers.render_user_template("delete_user.html", **kwargs)

    helpers.check_csrf()

    validator = helpers.Validator()

    if not users.is_admin():
        password = request.form["inputPassword"]
        validator.check_user_password(password)

    if not validator.error.empty():
        kwargs["error"] = validator.error
    else:
        kwargs.update(delete_and_logout_user(user_id))

    return helpers.render_user_template("delete_user.html", **kwargs)


@app.route("/account/search", methods=["POST"])
def search_account():
    helpers.check_admin_privileges()
    helpers.check_csrf()

    username = request.form["inputUsername"]
    selected_user_id = request.form["selectedUserId"]

    user = users.get_user_data_by_name(username)

    if not user:
        error = helpers.Error(
            {"inputUsername": f"Käyttäjää {username} ei löytynyt."})
        return show_account(selected_user_id, error=error)

    return redirect(f"/account/{user.id}")


def delete_and_logout_user(user_id):
    kwargs = {}
    try:
        users.delete_user(user_id)

        if not users.is_admin():
            users.logout()

        kwargs["message"] = "Käyttäjätili poistettiin onnistuneesti."
    except users.DeleteUserError as err:
        error = helpers.Error({"deleteAccount", err.__str__()})
        kwargs["error"] = error

    return kwargs
