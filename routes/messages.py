from flask import redirect, request
from flask_init import app
from routes import helpers
import messages
import users


@app.route("/message/post", methods=["POST"])
def post_message():
    helpers.abort_invalid_user_data()

    message = request.form["inputMessage"]

    if message:
        messages.add_message(users.get_logged_user_id(), message[:50])

    return redirect("/")
