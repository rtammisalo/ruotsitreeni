from flask_init import app
from routes import helpers
import users
import exercises
import messages


@app.route("/")
def index():
    user_id = users.get_logged_user_id()

    if user_id:
        return helpers.render_user_template("index.html",
                                            exercises=exercises.get_exercises(),
                                            messages=messages.get_last_messages(50))

    return helpers.render_login()
