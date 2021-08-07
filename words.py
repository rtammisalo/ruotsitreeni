from db import db


def get_words(exercise_id):
    sql = " ".join(("SELECT id, finnish_word, swedish_word",
                    "FROM words",
                    "WHERE exercise_id = :exercise_id"))
    return db.session.execute(sql, {"exercise_id": exercise_id}).fetchall()


def add_word(exercise_id, finnish, swedish, image_data):
    sql = " ".join(("INSERT INTO words (exercise_id, finnish_word, swedish_word, image_data)",
                    "VALUES (:exercise_id, :finnish, :swedish, :image)",
                    "RETURNING id"))
    result = db.session.execute(sql, {"exercise_id": exercise_id, "finnish": finnish,
                                      "swedish": swedish, "image": image_data})
    db.session.commit()

    return result.fetchone()[0]


def add_multiple_choices(word_id, choices):
    if not choices:
        return

    for choice in choices:
        sql = " ".join(("INSERT INTO answer_choices (word_id, wrong_answer)",
                        "VALUES (:word_id, :choice)"))
        db.session.execute(sql, {"word_id": word_id, "choice": choice})

    db.session.commit()
