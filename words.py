import random
from db import db

DEFAULT_SWEDISH_WORDS = {"igår", "idag", "imorgon", "timme", "kan", "göra",
                         "skratta", "se", "bra", "svår", "dålig", "utsökt",
                         "vatten", "huvud", "ben", "mage", "försäljare",
                         "liten", "långt",  "använda", "gå", "kommer", "stor",
                         "ljus", "förändring", "behöver", "bilden", "punkt",
                         "nära", "själv", "ny", "människa", "enligt", "gammal"}
RANDOM_WORD_CHOICES = 9


def get_word(word_id):
    sql = """SELECT id, finnish_word, swedish_word, image_data
             FROM words 
             WHERE id = :word_id"""
    return db.session.execute(sql, {"word_id": word_id}).fetchone()


def get_words(exercise_id):
    sql = """SELECT id, finnish_word, swedish_word
             FROM words
             WHERE exercise_id = :exercise_id"""
    return db.session.execute(sql, {"exercise_id": exercise_id}).fetchall()


def get_random_word(exercise_id):
    sql = """SELECT id, finnish_word, swedish_word, image_data
             FROM words WHERE exercise_id = :exercise_id
             ORDER BY RANDOM()
             LIMIT 1"""
    return db.session.execute(sql, {"exercise_id": exercise_id}).fetchone()


def get_random_swedish_words(excluded_word, word_count):
    sql = """SELECT swedish_word FROM words
             WHERE swedish_word != :excluded_word
             ORDER BY RANDOM() 
             LIMIT :word_count"""
    random_words_list = db.session.execute(
        sql, {"excluded_word": excluded_word, "word_count": word_count}).fetchall()
    random_words = set(map(lambda word_elem: word_elem[0], random_words_list))
    return random_words


def add_word(exercise_id, finnish, swedish, image_data):
    sql = """INSERT INTO words (exercise_id, finnish_word, swedish_word, image_data)
             VALUES (:exercise_id, :finnish, :swedish, :image)
             RETURNING id"""
    result = db.session.execute(sql, {"exercise_id": exercise_id, "finnish": finnish,
                                      "swedish": swedish, "image": image_data})
    db.session.commit()
    return result.fetchone()[0]


def update_word(word_id, finnish, swedish, image_data):
    sql = """UPDATE words
             SET finnish_word = :finnish, swedish_word = :swedish, image_data = :image_data
             WHERE id = :word_id"""
    parameters = {"word_id": word_id, "finnish": finnish,
                  "swedish": swedish, "image_data": image_data}
    db.session.execute(sql, parameters)
    db.session.commit()


def add_multiple_choices(word_id, choices):
    if not choices:
        return

    sql = """INSERT INTO answer_choices (word_id, wrong_answer)
             VALUES (:word_id, :choice)"""
    for choice in choices:
        db.session.execute(sql, {"word_id": word_id, "choice": choice})
    db.session.commit()


def update_multiple_choices(word_id, choices):
    sql = """DELETE FROM answer_choices
             WHERE word_id = :word_id"""
    db.session.execute(sql, {"word_id": word_id})
    db.session.commit()
    add_multiple_choices(word_id, choices)


def get_admin_defined_choices(word_id):
    sql = """SELECT wrong_answer
             FROM answer_choices
             WHERE word_id = :word_id"""
    return db.session.execute(sql, {"word_id": word_id}).fetchall()


def get_multiple_choices(word_id, swedish_word):
    choices = get_admin_defined_choices(word_id)

    if not choices:
        choices = get_random_choices(swedish_word, RANDOM_WORD_CHOICES)
    else:
        choices = list(map(lambda a: a[0], choices))

    choices.append(swedish_word)
    random.shuffle(choices)
    return choices


def get_random_choices(swedish_word, choices_count):
    words = get_random_swedish_words(swedish_word, choices_count)

    if len(words) < choices_count:
        default_words = DEFAULT_SWEDISH_WORDS.copy()
        default_words.discard(swedish_word)
        default_words = default_words.difference(words)
        add_count = min(choices_count - len(words), len(default_words))
        words = words.union(random.sample(default_words, add_count))

    return list(words)


def remove_word(word_id):
    sql = """DELETE FROM words
             WHERE id = :word_id"""
    db.session.execute(sql, {"word_id": word_id})
    db.session.commit()
