import os

SECRET_KEY = os.getenv("SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


def config_file_found():
    return os.path.isfile(".env")


def secret_key_set():
    if not SECRET_KEY:
        return False
    return True


def database_url_set():
    if not DATABASE_URL:
        return False
    return True
