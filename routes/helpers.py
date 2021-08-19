from flask import render_template, request, abort, make_response
from flask_init import app
import users
import exercises
import words


class Error:
    def __init__(self):
        self._messages = {}

    def add(self, error_type, error_message):
        if error_message:
            self._messages[error_type] = error_message

    def get(self, error_type):
        return self._messages.get(error_type, None)

    def get_all(self):
        return list(self._messages.values())

    def empty(self):
        return len(self._messages) == 0


@app.route("/image/<int:word_id>")
def show_image(word_id):
    image_data = words.get_word(word_id).image_data
    response = make_response(bytes(image_data))
    response.headers.set("Content-Type", "image/jpeg")

    return response


def render_login(error=None):
    return render_template("login.html", error=error)


def render_create_user(error=None):
    return render_template("create_user.html", password_pattern=users.PASSWORD_REGEX, error=error)


def render_user_template(template, **kwargs):
    kwargs["user_id"] = users.get_logged_user_id()
    kwargs["admin"] = users.is_admin()
    return render_template(template, **kwargs)


def abort_invalid_user_data(admin_required=False):
    try:
        csrf_token = request.form.get("csrf_token", None)

        if not csrf_token:
            raise users.UserValidationError

        users.validate_user(csrf_token, admin_required)

    except users.UserValidationError:
        abort(403)


def abort_non_admin():
    if not users.is_admin():
        abort(403)


def get_exercise_or_abort(exercise_id):
    # Handle aborts in routes module
    exercise = exercises.get_exercise(exercise_id)

    if not exercise:
        abort(404)

    return exercise
