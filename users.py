import secrets
import re
import string
from flask import session
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from db import db

ADMIN_ACCOUNT_TYPE = 0
USER_ACCOUNT_TYPE = 1


class LoginUserError(Exception):
    pass


class CreateUserError(Exception):
    pass


class UserValidationError(Exception):
    pass


def get_user_data(username):
    sql = " ".join(("SELECT id, password_hash, account_type",
                    "FROM users",
                    "WHERE username=:username AND visible=TRUE"))
    return db.session.execute(sql, {"username": username}).fetchone()


def login(username, password):
    user = get_user_data(username)

    if not user:
        raise LoginUserError("Virhe: kyseistä käyttäjänimeä ei ole olemassa.")

    if not check_password_hash(user["password_hash"], password):
        raise LoginUserError("Virhe: käyttäjänimi/salasana on väärin.")

    session["username"] = username
    session["user_id"] = user["id"]
    session["account_type"] = user["account_type"]
    session["csrf_token"] = secrets.token_hex(16)


def logout():
    del session["username"]
    del session["user_id"]
    del session["account_type"]
    del session["csrf_token"]


def validate_user(csrf_token, admin_required=False):
    if not get_logged_user_id():
        raise UserValidationError("User not logged in.")

    if get_csrf_token() != csrf_token:
        raise UserValidationError("CSRF token mismatch.")

    if admin_required and not is_admin():
        raise UserValidationError("User does not have admin privileges.")


def get_logged_user_id():
    return session.get("user_id", None)


def get_csrf_token():
    return session.get("csrf_token", None)


def get_account_type():
    return session.get("account_type", None)


def is_admin():
    if get_account_type() == ADMIN_ACCOUNT_TYPE:
        return True

    return False


def check_username(username):
    user = get_user_data(username)

    if user:
        raise CreateUserError("Virhe: kyseinen käyttäjänimi on jo olemassa.")

    if len(username) < 3:
        raise CreateUserError("Virhe: käyttäjänimi on liian lyhyt.")

    if len(username) > 12:
        raise CreateUserError("Virhe: käyttäjänimi on liian pitkä.")

    if not username.isalnum():
        raise CreateUserError("Virhe: käyttäjänimi sisältää vääriä merkkejä.")


def check_password(password):

    if len(password) < 6:
        raise CreateUserError("Virhe: salasana on liian lyhyt.")

    if len(password) > 20:
        raise CreateUserError("Virhe: salasana on liian pitkä.")

    regexp = f"^[a-zA-Z0-9{string.punctuation}]+$"
    if not re.search(regexp, password):
        raise CreateUserError("Virhe: salasana sisältää vääriä merkkejä.")


def create(username, password, account_type=USER_ACCOUNT_TYPE, auto_login=True):
    check_username(username)
    check_password(password)

    try:
        # Use join method when constructing SQL queries in order to
        # avoid missing whitespaces.
        sql = " ".join(("INSERT INTO users (username, password_hash, account_type, visible)",
                        "VALUES (:username, :password_hash, :account_type, TRUE)"))
        db.session.execute(sql, {"username": username, "password_hash": generate_password_hash(
            password), "account_type": account_type})
        db.session.commit()

        if auto_login:
            login(username, password)

    except SQLAlchemyError as err:
        raise CreateUserError("Virhe: käyttäjänimi on jo käytössä.") from err


def create_admin_account(username="admin", password="admin1"):
    try:
        if get_user_data(username):
            return

        create(username, password,
               account_type=ADMIN_ACCOUNT_TYPE, auto_login=False)
    except CreateUserError as err:
        print("Error: could not create admin account '" +
              username + "' with password '" + password + "'.")
        print(err)
