from flask import session, request, redirect
from flask_init import app
from routes import helpers
import words
import users
import answers
import exercises


@app.route("/exercise/<int:exercise_id>/word/<int:word_id>/answer", methods=["POST"])
def process_exercise_answer(exercise_id, word_id):
    helpers.check_user_privileges()
    helpers.check_csrf()

    answer = request.form["answer"]
    word = words.get_word(word_id)
    redirection = redirect(f"/exercise/{exercise_id}")

    if not answer or not word:
        return redirection

    answer = answer.strip()
    session["answer"] = answer
    session["correct_answer"] = word.swedish_word
    helpers.delete_exercise_question(exercise_id)
    used_multichoice = request.form["used_multichoice"]
    result = (answer == word.swedish_word)
    answers.add_answer(users.get_logged_user_id(),
                       word_id, used_multichoice, result)
    return redirection


@app.route("/exercise/<int:exercise_id>/word")
def show_words(exercise_id):
    helpers.check_admin_privileges()
    exercise = helpers.get_exercise_or_abort(exercise_id)
    exercise_words = words.get_words(exercise_id)
    use_multichoice = exercises.get_exercise_answer_style(exercise)
    return helpers.render_user_template_with_stats("create_word.html", exercise=exercise,
                                                   use_multichoice=use_multichoice,
                                                   words=exercise_words)


@app.route("/exercise/<int:exercise_id>/word/new", methods=["POST"])
def create_word(exercise_id):
    helpers.check_admin_privileges()
    helpers.check_csrf()
    exercise = helpers.get_exercise_or_abort(exercise_id)
    exercise_words = words.get_words(exercise_id)
    kwargs = {"exercise": exercise, "words": exercise_words,
              "use_multichoice": exercises.get_exercise_answer_style(exercise)}
    return process_word_input_form(exercise_id, kwargs)


def process_finnish_word(error):
    finnish_word = request.form.get("inputFinnishWord", None)
    finnish_word = finnish_word.strip()
    if not finnish_word:
        error.add("inputFinnishWord", "Suomenkielinen sana puuttuu.")
    return finnish_word


def process_swedish_word(error):
    swedish_word = request.form.get("inputSwedishWord", None)
    swedish_word = swedish_word.strip()
    if not swedish_word:
        error.add("inputSwedishWord", "Ruotsinkielinen sana puuttuu.")
    return swedish_word


def process_image_data(error, old_word_data=None):
    image_file = request.files.get("inputImage", None)
    if not image_file:
        if old_word_data:
            return old_word_data["image_data"]
        error.add("inputFile", "Kuvatiedosto puuttuu.")
        return ""

    filename = image_file.filename
    image_data = image_file.read()

    if not filename.endswith((".jpg")):
        error.add("inputFile", "Kuvatiedosto ei ole .jpg p????tteinen.")
    if len(image_data) > 150 * 1024:
        error.add("inputFileSize", "Tiedosto on suurempi kuin 150 kB.")

    return image_data


def process_multiple_choices():
    choices = request.form["inputMultipleChoice"].splitlines()
    return choices[:20]


def process_word_input_form(exercise_id, template_keywords, old_word_data=None):
    error = helpers.Error()
    finnish_word = process_finnish_word(error)
    swedish_word = process_swedish_word(error)
    image_data = process_image_data(error, old_word_data)
    choices = process_multiple_choices()

    if not error.empty():
        template_keywords["error"] = error
        if old_word_data:
            return helpers.render_user_template_with_stats("modify_word.html",
                                                           **template_keywords)
        return helpers.render_user_template_with_stats("create_word.html",
                                                       **template_keywords)

    if old_word_data:
        word_id = old_word_data["id"]
        words.update_word(word_id, finnish_word,
                          swedish_word, image_data)
        words.update_multiple_choices(word_id, choices)
        return redirect(f"/exercise/{exercise_id}/word")

    word_id = words.add_word(exercise_id, finnish_word,
                             swedish_word, image_data)
    words.add_multiple_choices(word_id, choices)
    return redirect(f"/exercise/{exercise_id}/word")


@app.route("/exercise/<int:exercise_id>/word/modify", methods=["POST"])
def modify_or_delete_word(exercise_id):
    helpers.check_admin_privileges()
    helpers.check_csrf()

    word_id = request.form["wordSelection"]
    if request.form.get("remove", None) is not None:
        return remove_word(exercise_id, word_id)

    return redirect(f"/exercise/{exercise_id}/word/{word_id}/modify")


def remove_word(exercise_id, word_id):
    words.remove_word(word_id)
    return redirect(f"/exercise/{exercise_id}/word")


@app.route("/exercise/<int:exercise_id>/word/<int:word_id>/modify", methods=["GET", "POST"])
def modify_word(exercise_id, word_id):
    helpers.check_admin_privileges()

    word_data = words.get_word(word_id)
    exercise = helpers.get_exercise_or_abort(exercise_id)
    choices = words.get_admin_defined_choices(word_id)
    exercise_words = words.get_words(exercise_id)
    kwargs = {"exercise": exercise, "words": exercise_words,
              "selected_word": word_data, "answer_choices": choices,
              "use_multichoice": exercises.get_exercise_answer_style(exercise)}

    if request.method == "GET":
        return helpers.render_user_template_with_stats("modify_word.html", **kwargs)

    helpers.check_csrf()
    return process_word_input_form(exercise_id, kwargs, word_data)
