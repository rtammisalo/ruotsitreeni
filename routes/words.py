from flask import session, request, redirect
from flask_init import app
from routes import helpers
import words
import users


@app.route("/exercise/<int:exercise_id>/word/<int:word_id>/answer", methods=["POST"])
def process_exercise_answer(exercise_id, word_id):
    helpers.abort_invalid_user_data()

    answer = request.form["answer"]
    word = words.get_word(word_id)
    redirection = redirect(f"/exercise/{exercise_id}")

    if not answer or not word:
        return redirection

    session["answer"] = answer
    session["correct_answer"] = word.swedish_word
    result = (answer == word.swedish_word)
    words.add_answer(users.get_logged_user_id(), word_id, result)
    return redirection


@app.route("/exercise/<int:exercise_id>/word")
def show_words(exercise_id):
    helpers.abort_non_admin()
    exercise = helpers.get_exercise_or_abort(exercise_id)
    exercise_words = words.get_words(exercise_id)
    return helpers.render_user_template("word.html", exercise=exercise, words=exercise_words)


@app.route("/exercise/<int:exercise_id>/word/new", methods=["POST"])
def create_word(exercise_id):
    helpers.abort_invalid_user_data(admin_required=True)

    exercise = helpers.get_exercise_or_abort(exercise_id)
    finnish_word = request.form["inputFinnishWord"]
    swedish_word = request.form["inputSwedishWord"]
    image_file = request.files["inputImage"]
    image_data = image_file.read()
    filename = image_file.filename
    error = helpers.Error()

    if not finnish_word:
        error.add("inputFinnishWord", "Suomenkielinen sana puuttuu.")

    if not swedish_word:
        error.add("inputSwedishWord", "Ruotsinkielinen sana puuttuu.")

    if not image_file or not filename.endswith((".jpg")):
        error.add("inputFile", "Tiedosto ei ole tyyppiä jpg.")

    if len(image_data) > 150 * 1024:
        error.add("inputFileSize", "Tiedosto on suurempi kuin 150 kB.")

    if not error.empty():
        return helpers.render_user_template("word.html", exercise=exercise,
                                            words=words.get_words(exercise_id),
                                            error=error)

    choices = request.form["inputMultipleChoice"].splitlines()
    word_id = words.add_word(exercise_id, finnish_word,
                             swedish_word, image_data)
    words.add_multiple_choices(word_id, choices[:20])
    return redirect(f"/exercise/{exercise_id}/word")
