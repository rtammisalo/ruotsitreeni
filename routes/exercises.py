from flask import session, request, redirect
from flask_init import app
from routes import helpers
import users
import exercises
import words


@ app.route("/exercise/<int:exercise_id>/visible")
def flip_exercise_visibility(exercise_id):
    helpers.abort_non_admin()
    exercise = helpers.get_exercise_or_abort(exercise_id)
    exercises.set_visible(exercise_id, not exercise.visible)
    return redirect(f"/exercise/{exercise_id}")


@app.route("/exercise/<int:exercise_id>/flip_answer_style", methods=["POST"])
def flip_answer_style(exercise_id):
    helpers.abort_invalid_user_data()
    exercise = helpers.get_exercise_or_abort(exercise_id)
    exercises.flip_exercise_answer_style(exercise, users.get_logged_user_id())
    return redirect(f"/exercise/{exercise_id}")


@ app.route("/exercise/new", methods=["GET", "POST"])
def create_exercise():
    helpers.abort_non_admin()

    if request.method == "GET":
        return helpers.render_user_template("create_exercise.html")

    if request.method == "POST":
        helpers.abort_invalid_user_data(admin_required=True)

        title = request.form["inputExerciseTitle"]
        topic = request.form["inputExerciseTopic"]

        try:
            exercise_id = exercises.create(title, topic)
            return redirect(f"/exercise/{exercise_id}")
        except exercises.CreateExerciseError as err:
            return helpers.render_user_template("create_exercise.html", error=err)

    return redirect("/")


@ app.route("/exercise/<int:exercise_id>")
def show_exercise(exercise_id):
    if not users.get_logged_user_id():
        return redirect("/")

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
