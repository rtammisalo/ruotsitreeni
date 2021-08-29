from sqlalchemy.exc import SQLAlchemyError
from db import db


def get_user_statistics(user_id, exercise_id=None):
    try:
        if exercise_id:
            sql = """SELECT *,
                            (results.correct * 100.0 / results.all) AS correct_percent,
                            (results.wrong * 100.0 / results.all) AS wrong_percent
                     FROM (SELECT COUNT(*) AS all,
                           (COUNT(*) FILTER (WHERE result)) AS correct,
                           (COUNT(*) FILTER (WHERE NOT result)) AS wrong
                           FROM answers
                           LEFT JOIN words
                                  ON answers.word_id = words.id
                           WHERE (words.exercise_id = :exercise_id AND
                                  user_id = :user_id)) AS results"""
        else:
            sql = """SELECT *,
                            (results.correct * 100.0 / results.all) AS correct_percent,
                            (results.wrong * 100.0 / results.all) AS wrong_percent
                     FROM (SELECT COUNT(*) AS all,
                           (COUNT(*) FILTER (WHERE result)) AS correct,
                           (COUNT(*) FILTER (WHERE NOT result)) AS wrong
                           FROM answers
                           WHERE user_id = :user_id) AS results"""

        parameters = {"user_id": user_id, "exercise_id": exercise_id}
        return db.session.execute(sql, parameters).fetchone()
    except SQLAlchemyError:
        return {"all": 0, "correct": 0, "wrong": 0, "correct_percent": 0.0, "wrong_percent": 0.0}
