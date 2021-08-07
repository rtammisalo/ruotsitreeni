from flask import render_template, request, redirect, abort
from flask_init import app
import users
import exercises
import words

USERNAME_HELP_STRING = "Käyttäjätunnus tulee olla 3 - 12 merkkiä pitkä ja voi sisältää kirjaimia ja numeroita."
PASSWORD_HELP_STRING = "Salasanan tulee olla 6-20 merkkiä pitkä ja voi sisältää kirjaimia, erikoismerkkejä ja numeroita."


@app.route("/")
def index():
    user_id = users.get_logged_user_id()

    if user_id:
        kwargs = {"user_id": user_id, "admin": users.is_admin(), "error": None,
                  "exercises": exercises.get_exercises()}
        return render_template("index.html", **kwargs)

    return render_login()


@app.route("/exercise/<int:exercise_id>/word")
def show_words(exercise_id):
    if not users.is_admin():
        abort(403)

    exercise = get_exercise_or_abort(exercise_id)
    exercise_words = words.get_words(exercise_id)

    return render_template("word.html", exercise=exercise, words=exercise_words)


@app.route("/exercise/<int:exercise_id>/word/new", methods=["POST"])
def create_word(exercise_id):
    abort_invalid_user_data(admin_required=True)

    exercise = get_exercise_or_abort(exercise_id)
    finnish_word = request.form["inputFinnishWord"]
    swedish_word = request.form["inputSwedishWord"]
    image_file = request.files["inputImage"]
    image_data = image_file.read()
    filename = image_file.filename
    error_msg = ""

    if not image_file or not filename.endswith((".jpg", ".png")):
        error_msg = "Virhe: tiedosto ei ole tyyppiä jpeg tai png."

    if len(image_data) > 150 * 1024:
        error_msg = "Virhe: tiedosto on suurempi kuin 150 kB."

    if not finnish_word:
        error_msg = "Virhe: suomenkielinen sana puuttuu."

    if not swedish_word:
        error_msg = "Virhe: ruotsinkielinen sana puuttuu."

    if error_msg:
        return render_template("word.html", exercise=exercise,
                               words=words.get_words(exercise_id),
                               error=error_msg)
    
    words.add_word(exercise_id, finnish_word, swedish_word, image_data)

    return redirect(f"/exercise/{exercise_id}/word")



@ app.route("/exercise/<int:exercise_id>/visible")
def flip_exercise_visibility(exercise_id):
    if not users.is_admin():
        abort(403)

    exercise = get_exercise_or_abort(exercise_id)
    exercises.set_visible(exercise_id, not exercise.visible)
    return redirect(f"/exercise/{exercise_id}")


@ app.route("/exercise/new", methods=["GET", "POST"])
def create_exercise():
    if not users.is_admin():
        abort(403)

    if request.method == "GET":
        return render_template("create_exercise.html")

    if request.method == "POST":
        abort_invalid_user_data(admin_required=True)

        title = request.form["inputExerciseTitle"]
        topic = request.form["inputExerciseTopic"]

        try:
            exercise_id = exercises.create(title, topic)
            return redirect(f"/exercise/{exercise_id}")
        except exercises.CreateExerciseError as err:
            return render_template("create_exercise.html", error=err)


@ app.route("/exercise/<int:exercise_id>")
def show_exercise(exercise_id):
    if not users.get_logged_user_id():
        return redirect("/")

    exercise = get_exercise_or_abort(exercise_id)

    return render_template("exercise.html", admin=users.is_admin(), exercise=exercise)


@ app.route("/login", methods=["POST"])
def login():
    if users.get_logged_user_id():
        return redirect("/")

    username = request.form["inputUsername"]
    password = request.form["inputPassword"]

    try:
        users.login(username, password)
    except users.LoginUserError as err:
        return render_login(error=err)

    return redirect("/")


@ app.route("/create_user", methods=["POST", "GET"])
def create_user():
    if users.get_logged_user_id():
        return redirect("/")

    if request.method == "GET":
        return render_create_user()

    try:
        username = request.form["inputUsername"]
        password = request.form["inputPassword"]

        users.create(username, password)
    except users.CreateUserError as err:
        return render_create_user(err)

    return redirect("/")


@ app.route("/logout")
def logout_user():
    if users.get_logged_user_id():
        users.logout()

    return redirect("/")


def render_login(error=None):
    return render_template("login.html", error=error)


def render_create_user(error=None):
    return render_template("create_user.html", username_help=USERNAME_HELP_STRING,
                           password_help=PASSWORD_HELP_STRING, error=error)


def abort_invalid_user_data(admin_required=False):
    try:
        csrf_token = request.form.get("csrf_token", None)

        if not csrf_token:
            raise users.UserValidationError

        users.validate_user(csrf_token, admin_required)

    except users.UserValidationError as err:
        abort(403)


def get_exercise_or_abort(exercise_id):
    # Handle aborts in routes module
    exercise = exercises.get_exercise(exercise_id)

    if not exercise:
        abort(404)

    return exercise
