from flask_init import app
from routes import helpers
import users


@app.route("/")
def index():
    user_id = users.get_logged_user_id()

    if user_id:
        helpers.check_user_privileges()
        return helpers.render_main_view()

    return helpers.render_login()
