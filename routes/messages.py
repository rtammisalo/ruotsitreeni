from flask import redirect, request
from flask.templating import render_template
from flask_init import app
from routes import helpers
import messages
import users

MAX_MESSAGE_LEN = 100


@app.route("/message/post", methods=["POST"])
def post_message():
    helpers.check_user_privileges()
    helpers.check_csrf()

    message = request.form["inputMessage"]
    message = message.strip()

    if message:
        messages.add_message(users.get_logged_user_id(),
                             message[:MAX_MESSAGE_LEN])

    return redirect("/")


@app.route("/message/<int:message_id>/delete", methods=["POST", "GET"])
def delete_message(message_id):
    helpers.check_admin_privileges()

    if request.method == "GET":
        message = messages.get_message(message_id)
        if not message:
            return redirect("/")
        return helpers.render_main_view(delete_message=message)

    helpers.check_csrf()

    messages.delete_message(message_id)

    return redirect("/")
