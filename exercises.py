from sqlalchemy.exc import SQLAlchemyError
from db import db

ANSWER_STYLE_MULTICHOICE = 0
ANSWER_STYLE_INPUT = 1


class CreateExerciseError(Exception):
    pass


def get_exercises():
    sql = """SELECT id, title, topic, created_at, visible
             FROM exercises
             ORDER BY title"""
    return db.session.execute(sql).fetchall()


def get_exercise(exercise_id, user_id):
    sql = """SELECT exercises.id, title, topic, created_at, visible, use_multichoice
             FROM exercises
             LEFT JOIN (SELECT user_id, exercise_id, use_multichoice
                        FROM exercise_answer_styles
                        WHERE user_id = :user_id) AS eas
                    ON exercises.id = eas.exercise_id
             WHERE exercises.id = :exercise_id"""
    exercise = db.session.execute(
        sql, {"exercise_id": exercise_id, "user_id": user_id}).fetchone()
    print(exercise)
    return exercise


def flip_exercise_answer_style(exercise, user_id):
    sql = """UPDATE exercise_answer_styles
             SET use_multichoice = :use_multichoice
             WHERE user_id = :user_id AND exercise_id = :exercise_id
             RETURNING id
             """
    parameters = {"use_multichoice": not get_exercise_answer_style(exercise),
                  "user_id": user_id, "exercise_id": exercise.id}
    result = db.session.execute(sql, parameters)

    if not result.fetchone():
        sql = """INSERT INTO exercise_answer_styles
                 (user_id, exercise_id, use_multichoice)
                 VALUES (:user_id, :exercise_id, :use_multichoice)"""
        db.session.execute(sql, parameters)

    db.session.commit()


def get_exercise_answer_style(exercise):
    if exercise.use_multichoice is not None:
        return exercise.use_multichoice
    return True


def set_visible(exercise_id, visible):
    sql = """UPDATE exercises
             SET visible = :visible
             WHERE id = :exercise_id"""
    db.session.execute(sql, {"exercise_id": exercise_id, "visible": visible})
    db.session.commit()


def create(title, topic):
    try:
        sql = """INSERT INTO exercises (title, topic, created_at, visible)
                 VALUES (:title, :topic, NOW(), FALSE)
                 RETURNING id"""
        result = db.session.execute(sql, {"title": title, "topic": topic})
        db.session.commit()
        return result.fetchone()[0]
    except SQLAlchemyError as err:
        raise CreateExerciseError("Harjoituksen nimi on jo käytössä.") from err
