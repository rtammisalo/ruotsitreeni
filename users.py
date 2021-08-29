import secrets
import re
from flask import session
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from db import db

ADMIN_ACCOUNT_TYPE = 0
USER_ACCOUNT_TYPE = 1
PASSWORD_REGEX = r"^(\w|[^\w ]){6,20}$"


class UserCredentialsError(Exception):
    pass


class CreateUserError(Exception):
    pass


class DeleteUserError(Exception):
    pass


class UserValidationError(Exception):
    pass


def get_user_data_by_name(username):
    sql = """SELECT id, username, password_hash, account_type, created_at
             FROM users
             WHERE UPPER(username) = :username"""
    return db.session.execute(sql, {"username": username.upper()}).fetchone()


def get_user_data_by_id(user_id):
    sql = """SELECT id, username, password_hash, account_type, created_at
             FROM users
             WHERE id=:user_id"""
    return db.session.execute(sql, {"user_id": user_id}).fetchone()


def check_user_password(user_data, password):
    if not user_data:
        raise UserCredentialsError(
            "Kyseistä käyttäjänimeä ei ole olemassa.")

    if not check_password_hash(user_data["password_hash"], password):
        raise UserCredentialsError("Käyttäjänimi/salasana on väärin.")


def change_user_password_by_id(user_id, new_password):
    try:
        sql = """UPDATE users
                 SET password_hash = :password_hash
                 WHERE id = :user_id"""
        db.session.execute(
            sql, {"password_hash": generate_password_hash(new_password), "user_id": user_id})
        db.session.commit()
    except SQLAlchemyError as err:
        raise UserCredentialsError(
            "Salasanan vaihto epäonnistui.") from err


def login(username, password):
    user = get_user_data_by_name(username)

    check_user_password(user, password)

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


def get_username():
    return session.get("username", None)


def get_csrf_token():
    return session.get("csrf_token", None)


def get_account_type():
    return session.get("account_type", None)


def is_admin():
    if get_account_type() == ADMIN_ACCOUNT_TYPE:
        return True
    return False


def validate_username(username):
    user = get_user_data_by_name(username)

    if user:
        return "Käyttäjänimi on jo olemassa."

    if len(username) < 3:
        return "Käyttäjänimi on liian lyhyt."

    if len(username) > 12:
        return "Käyttäjänimi on liian pitkä."

    if not username.isalnum():
        return "Käyttäjänimi sisältää vääriä merkkejä."

    return None


def validate_password(password):

    if len(password) < 6:
        return "Salasana on liian lyhyt."

    if len(password) > 20:
        return "Salasana on liian pitkä."

    if not re.search(PASSWORD_REGEX, password):
        print(password)
        return "Salasana sisältää vääriä merkkejä."

    return None


def create(username, password, account_type=USER_ACCOUNT_TYPE, auto_login=True):

    try:
        sql = """INSERT INTO users (username, password_hash, account_type, created_at)
                 VALUES (:username, :password_hash, :account_type, NOW())"""
        db.session.execute(sql, {"username": username, "password_hash": generate_password_hash(
            password), "account_type": account_type})
        db.session.commit()

        if auto_login:
            login(username, password)

    except SQLAlchemyError as err:
        raise CreateUserError("Käyttäjänimi on jo käytössä.") from err


def create_admin_account(username="admin", password="admin1"):
    try:
        if get_user_data_by_name(username):
            return

        create(username, password,
               account_type=ADMIN_ACCOUNT_TYPE, auto_login=False)
    except CreateUserError as err:
        print("Error: could not create admin account '" +
              username + "' with password '" + password + "'.")
        print(err)


def delete_user(user_id):
    try:
        sql = """DELETE FROM users
                 WHERE id = :user_id"""
        db.session.execute(sql, {"user_id": user_id})
        db.session.commit()
    except SQLAlchemyError as err:
        raise DeleteUserError("Käyttäjätilin tuhoaminen epäonnistui.") from err
