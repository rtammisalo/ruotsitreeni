from sqlalchemy.exc import SQLAlchemyError
from db import db


def add_answer(user_id, word_id, used_multichoice, result):
    sql = """INSERT INTO answers (user_id, word_id, used_multichoice, result)
             VALUES (:user_id, :word_id, :used_multichoice, :result)"""
    db.session.execute(
        sql, {"user_id": user_id, "word_id": word_id,
              "used_multichoice": used_multichoice, "result": result})
    db.session.commit()


def _get_sql_query_base(where_stmt, exercise_id=None):
    # Use only internally to avoid copy-pasteing the same big sql queries.
    if exercise_id:
        sql = f"""SELECT results.all AS all, results.correct AS correct,
                        results.wrong AS wrong,
                        (results.correct * 100.0 / results.all) AS correct_percent,
                        (results.wrong * 100.0 / results.all) AS wrong_percent
                 FROM (SELECT COUNT(*) AS all,
                        (COUNT(*) FILTER (WHERE result)) AS correct,
                        (COUNT(*) FILTER (WHERE NOT result)) AS wrong
                        FROM answers
                        LEFT JOIN words
                               ON answers.word_id = words.id
                        WHERE ( {where_stmt} )) AS results"""
    else:
        sql = f"""SELECT results.all AS all, results.correct AS correct,
                         results.wrong AS wrong,
                         (results.correct * 100.0 / results.all) AS correct_percent,
                         (results.wrong * 100.0 / results.all) AS wrong_percent
                  FROM (SELECT COUNT(*) AS all,
                        (COUNT(*) FILTER (WHERE result)) AS correct,
                        (COUNT(*) FILTER (WHERE NOT result)) AS wrong
                        FROM answers
                        WHERE ( {where_stmt} )) AS results"""
    return sql


def get_all_user_statistics(user_id, exercise_id=None):
    if exercise_id:
        where = """words.exercise_id = :exercise_id AND
                   user_id = :user_id"""
    else:
        where = """user_id = :user_id"""

    sql = _get_sql_query_base(where, exercise_id)
    parameters = {"user_id": user_id, "exercise_id": exercise_id}
    return _get_statistics(sql, parameters)


def get_multichoice_user_statistics(user_id, exercise_id=None):
    if exercise_id:
        where = """words.exercise_id = :exercise_id AND
                   user_id = :user_id AND
                   used_multichoice = TRUE"""
    else:
        where = """user_id = :user_id AND
                   used_multichoice = TRUE"""

    sql = _get_sql_query_base(where, exercise_id)
    parameters = {"user_id": user_id, "exercise_id": exercise_id}
    return _get_statistics(sql, parameters)


def get_input_user_statistics(user_id, exercise_id=None):
    if exercise_id:
        where = """words.exercise_id = :exercise_id AND
                   user_id = :user_id AND
                   used_multichoice = FALSE"""
    else:
        where = """user_id = :user_id AND
                   used_multichoice = FALSE"""

    sql = _get_sql_query_base(where, exercise_id)
    parameters = {"user_id": user_id, "exercise_id": exercise_id}
    return _get_statistics(sql, parameters)


def _get_statistics(sql, parameters):
    try:
        return db.session.execute(sql, parameters).fetchone()
    except SQLAlchemyError:
        return {"all": 0, "correct": 0, "wrong": 0, "correct_percent": 0.0, "wrong_percent": 0.0}
