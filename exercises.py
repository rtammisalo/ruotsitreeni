from sqlalchemy.exc import SQLAlchemyError
from db import db


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
    return exercise


def delete_exercise(exercise_id):
    sql = """DELETE FROM exercises
             WHERE id = :exercise_id"""
    db.session.execute(sql, {"exercise_id": exercise_id})
    db.session.commit()


def get_dict_from_exercise(exercise, new_title=None, new_topic=None):
    exercise_dict = {"id": exercise["id"], "title": exercise["title"],
                     "topic": exercise["topic"], "created_at": exercise["created_at"],
                     "visible": exercise["visible"]}
    if new_title is not None:
        exercise_dict["title"] = new_title
    if new_topic is not None:
        exercise_dict["topic"] = new_topic
    return exercise_dict


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
        raise ValueError("Harjoituksen nimi on jo käytössä.") from err


def update(exercise_id, new_title, new_topic):
    try:
        sql = """UPDATE exercises
                 SET title = :new_title, topic = :new_topic
                 WHERE id = :exercise_id"""
        parameters = {"new_title": new_title, "new_topic": new_topic,
                      "exercise_id": exercise_id}
        db.session.execute(sql, parameters)
        db.session.commit()
    except SQLAlchemyError as err:
        raise ValueError("Harjoituksen nimi on jo käytössä.") from err
