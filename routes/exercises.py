from flask import session, request, redirect
from flask_init import app
from routes import helpers
import users
import exercises
import words


@app.route("/exercise/<int:exercise_id>/modify", methods=["GET", "POST"])
def modify_exercise(exercise_id):
    helpers.check_admin_privileges()
    exercise = exercises.get_exercise(exercise_id, users.get_logged_user_id())
    if not exercise:
        helpers.abort(404)

    if request.method == "GET":
        return helpers.render_user_template("modify_exercise.html", exercise=exercise)

    helpers.check_csrf()
    try:
        title, topic = read_exercise_form()
        exercises.update(exercise_id, title, topic)
        return redirect(f"/exercise/{exercise_id}")
    except ValueError as err:
        exercise = exercises.get_dict_from_exercise(exercise, title, topic)
        return helpers.render_user_template("modify_exercise.html",
                                            exercise=exercise, error=err)


def read_exercise_form():
    title = request.form["inputExerciseTitle"]
    topic = request.form["inputExerciseTopic"]
    return title, topic


@app.route("/exercise/<int:exercise_id>/visible", methods=["POST"])
def flip_exercise_visibility(exercise_id):
    helpers.check_admin_privileges()
    helpers.check_csrf()
    exercise = helpers.get_exercise_or_abort(exercise_id)
    exercises.set_visible(exercise_id, not exercise.visible)
    return redirect(f"/exercise/{exercise_id}")


@app.route("/exercise/<int:exercise_id>/flip_answer_style", methods=["POST"])
def flip_answer_style(exercise_id):
    helpers.check_user_privileges()
    helpers.check_csrf()
    exercise = helpers.get_exercise_or_abort(exercise_id)
    exercises.flip_exercise_answer_style(exercise, users.get_logged_user_id())
    return redirect(f"/exercise/{exercise_id}")


@ app.route("/exercise/new", methods=["GET", "POST"])
def create_exercise():
    helpers.check_admin_privileges()

    if request.method == "GET":
        return helpers.render_user_template("create_exercise.html")

    if request.method == "POST":
        helpers.check_csrf()

        title, topic = read_exercise_form()

        try:
            exercise_id = exercises.create(title, topic)
            return redirect(f"/exercise/{exercise_id}")
        except exercises.CreateExerciseError as err:
            return helpers.render_user_template("create_exercise.html", error=err)

    return redirect("/")


@ app.route("/exercise/<int:exercise_id>")
def show_exercise(exercise_id):
    helpers.check_user_privileges()

    exercise = helpers.get_exercise_or_abort(exercise_id)
    word = words.get_random_word(exercise_id)
    choices = None
    answer = session.get("answer", None)
    correct_answer = session.get("correct_answer", None)

    if answer and correct_answer:
        del session["answer"]
        del session["correct_answer"]

    if word:
        choices = words.get_multiple_choices(word.id, word.swedish_word)

    kwargs = {"exercise": exercise, "word": word, "multiple_choices": choices,
              "answer": answer, "correct_answer": correct_answer,
              "use_multichoice": exercises.get_exercise_answer_style(exercise)}
    return helpers.render_user_template("exercise.html", **kwargs)


@app.route("/exercise/<int:exercise_id>/delete", methods=["POST", "GET"])
def delete_exercise(exercise_id):
    helpers.check_admin_privileges()

    exercise = helpers.get_exercise_or_abort(exercise_id)
    if request.method == "GET":
        return helpers.render_user_template("delete_exercise.html", selected_exercise=exercise)

    helpers.check_csrf()
    exercises.delete_exercise(exercise_id)
    message = f"Harjoitus {exercise['title']} on poistettu."
    return helpers.render_user_template("delete_exercise.html", message=message)
