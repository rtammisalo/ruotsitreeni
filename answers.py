from sqlalchemy.exc import SQLAlchemyError
from db import db


def get_user_statistics(user_id, exercise_id=None):
    try:
        sql = " ".join(("SELECT *, ",
                        "(CAST(results.correct AS FLOAT) / results.all) AS correct_percent,",
                        "(CAST(results.wrong AS FLOAT) / results.all) AS wrong_percent",
                        "FROM (SELECT COUNT(*) AS all, (COUNT(*) FILTER (WHERE result)) AS correct,",
                        "(COUNT(*) FILTER (WHERE NOT result)) AS wrong FROM answers"))
        parameters = {"user_id": user_id}

        if exercise_id:
            sql = " ".join((sql, "LEFT JOIN words ON answers.word_id = words.id",
                            "WHERE words.exercise_id = :exercise_id AND"))
            parameters["exercise_id"] = exercise_id
        else:
            sql = " ".join((sql, "WHERE"))

        sql = " ".join((sql, "user_id = :user_id", ") AS results"))

        return db.session.execute(sql, parameters).fetchone()
    except SQLAlchemyError:
        return {"all": 0, "correct": 0, "wrong": 0, "correct_percent": 0.0, "wrong_percent": 0.0}
