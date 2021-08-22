from flask import redirect, request
from flask.templating import render_template
from flask_init import app
from routes import helpers
import messages
import users

MAX_MESSAGE_LEN = 100


@app.route("/message/post", methods=["POST"])
def post_message():
    helpers.abort_invalid_user_data()

    message = request.form["inputMessage"]
    message = message.strip()

    if message:
        messages.add_message(users.get_logged_user_id(),
                             message[:MAX_MESSAGE_LEN])

    return redirect("/")


@app.route("/message/<int:message_id>/delete", methods=["POST", "GET"])
def delete_message(message_id):
    helpers.abort_non_admin()

    if request.method == "GET":
        message = messages.get_message(message_id)
        if not message:
            return redirect("/")
        return helpers.render_main_view(delete_message=message)

    helpers.abort_invalid_user_data(admin_required=True)

    messages.delete_message(message_id)

    return redirect("/")
