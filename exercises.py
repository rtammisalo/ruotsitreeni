from sqlalchemy.exc import SQLAlchemyError
from db import db


class CreateExerciseError(Exception):
    pass


def get_exercises():
    sql = " ".join(("SELECT id, title, topic, created_at, visible",
                    "FROM exercises",
                    "ORDER BY title"))
    return db.session.execute(sql).fetchall()


def get_exercise(exercise_id):
    sql = " ".join(("SELECT id, title, topic, created_at, visible",
                    "FROM exercises",
                    "WHERE id = :exercise_id"))
    exercise_id = db.session.execute(
        sql, {"exercise_id": exercise_id}).fetchone()
    return exercise_id


def set_visible(exercise_id, visible):
    sql = " ".join(("UPDATE exercises",
                    "SET visible = :visible",
                    "WHERE id = :exercise_id"))
    db.session.execute(sql, {"exercise_id": exercise_id, "visible": visible})
    db.session.commit()


def create(title, topic):
    try:
        sql = " ".join(("INSERT INTO exercises (title, topic, created_at, visible)",
                        "VALUES (:title, :topic, NOW(), FALSE)",
                        "RETURNING id"))
        result = db.session.execute(sql, {"title": title, "topic": topic})
        db.session.commit()
        return result.fetchone()[0]
    except SQLAlchemyError as err:
        raise CreateExerciseError("Virhe: harjoituksen nimi on jo käytössä.") from err
