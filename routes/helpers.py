from flask import render_template, request, abort, make_response, session
from flask_init import app
import users
import exercises
import words
import messages
import answers


class Error:
    def __init__(self, errors_dict=None):
        if not errors_dict:
            errors_dict = {}
        self._messages = errors_dict

    def add(self, error_type, error_message):
        if error_message:
            self._messages[error_type] = error_message

    def get(self, error_type):
        return self._messages.get(error_type, None)

    def get_all(self):
        return list(self._messages.values())

    def empty(self):
        return len(self._messages) == 0


class Validator:
    def __init__(self):
        self.error = Error()

    def check_repeat_password(self, password, password_again):
        if password != password_again:
            self.error.add("inputPasswordAgain", "Salasanat eivät ole samat.")

    def check_user_password_by_id(self, user_id, password):
        user = users.get_user_data_by_id(user_id)

        try:
            users.check_user_password(user, password)
        except ValueError as err:
            self.error.add("inputPassword", err.__str__())

    def check_user_password(self, password):
        self.check_user_password_by_id(users.get_logged_user_id(), password)

    def validate_username(self, username):
        error = users.validate_username(username)
        if error:
            self.error.add("inputUsername", error)

    def validate_password(self, password):
        error = users.validate_password(password)
        if error:
            self.error.add("inputPassword", error)


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


def render_main_view(**kwargs):
    return render_user_template("index.html", exercises=exercises.get_exercises(),
                                messages=messages.get_last_messages(50, users.is_admin()), **kwargs)


def render_user_template(template, **kwargs):
    kwargs["user_id"] = users.get_logged_user_id()
    kwargs["username"] = users.get_username()
    kwargs["admin"] = users.is_admin()
    return render_template(template, **kwargs)


def render_user_template_with_stats(template, exercise, use_multichoice, **kwargs):
    user_id = users.get_logged_user_id()
    if use_multichoice:
        stats = answers.get_multichoice_user_statistics(user_id, exercise.id)
    else:
        stats = answers.get_input_user_statistics(user_id, exercise.id)
    kwargs["statistics"] = stats
    kwargs["exercise"] = exercise
    kwargs["use_multichoice"] = use_multichoice
    return render_user_template(template, **kwargs)


def abort_non_admin():
    if not users.is_admin():
        abort(403)


def abort_invalid_user(correct_user_id):
    if users.get_logged_user_id() != correct_user_id and not users.is_admin():
        abort(403)


def get_exercise_or_abort(exercise_id):
    # Handle aborts in routes module
    exercise = exercises.get_exercise(exercise_id, users.get_logged_user_id())

    if not exercise:
        abort(404)

    return exercise


def check_user_privileges(required_user_id=None):
    session_user_id = users.get_logged_user_id()
    if not session_user_id:
        abort(403)
    user_data = users.get_user_data_by_id(session_user_id)
    if not user_data:
        users.logout()
        abort(403)
    if session_user_id != user_data["id"]:
        abort(403)
    if required_user_id:
        abort_invalid_user(required_user_id)


def check_admin_privileges():
    check_user_privileges()
    abort_non_admin()


def check_csrf():
    form_csrf_token = request.form.get("csrf_token", None)
    session_csrf_token = users.get_csrf_token()
    if not form_csrf_token:
        abort(403)
    if form_csrf_token != session_csrf_token:
        abort(403)


def _get_current_word_ids():
    if not session.get("current_word_ids", None):
        session["current_word_ids"] = {}
    return session["current_word_ids"]


def get_exercise_question(exercise_id):
    current_word_ids = _get_current_word_ids()
    word_id = current_word_ids.get(str(exercise_id), None)
    if not word_id:
        word = words.get_random_word(exercise_id)
        if word:
            current_word_ids[str(exercise_id)] = word["id"]
            # Without this the session changes are lost after redirect.
            session.modified = True  # pylint: disable=assigning-non-slot
    else:
        word = words.get_word(word_id)
    return word


def delete_exercise_question(exercise_id):
    current_word_ids = _get_current_word_ids()
    if current_word_ids.get(str(exercise_id), None):
        del current_word_ids[str(exercise_id)]
        session.modified = True  # pylint: disable=assigning-non-slot
