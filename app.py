from flask_init import app
import config
import routes
import user

if not config.config_file_found():
    print("Error: Couldn't find config file.")

if not config.secret_key_set():
    print("Error: Secret key was not provided.")

if not config.database_url_set():
    print("Error: Database URL was not provided.")

app.secret_key = config.SECRET_KEY

# At start, try to create the admin account described in the dotenv.
user.create_admin_account(config.ADMIN_USERNAME, config.ADMIN_PASSWORD)