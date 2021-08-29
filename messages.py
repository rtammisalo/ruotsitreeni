from db import db


def get_last_messages(message_count, show_invisible):
    if show_invisible:
        sql = """SELECT messages.id AS id, users.username AS username,
                        messages.created_at AS created_at, content,
                        messages.visible AS visible
                 FROM messages
                 LEFT JOIN users
                        ON user_id = users.id
                 ORDER BY created_at DESC
                 LIMIT :message_count"""
    else:
        sql = """SELECT messages.id AS id, users.username AS username,
                        messages.created_at AS created_at, content, 
                        messages.visible AS visible
                 FROM messages
                 LEFT JOIN users
                        ON user_id = users.id
                 WHERE messages.visible = TRUE
                 ORDER BY created_at DESC
                 LIMIT :message_count"""

    parameters = {"message_count": message_count}
    messages = db.session.execute(sql, parameters).fetchall()
    messages.reverse()
    return messages


def add_message(user_id, message):
    sql = """INSERT INTO messages (user_id, created_at, content, visible)
             VALUES (:user_id, NOW(), :content, TRUE)"""
    db.session.execute(sql, {"user_id": user_id, "content": message})
    db.session.commit()


def delete_message(message_id):
    sql = """UPDATE messages
             SET visible = FALSE
             WHERE id = :message_id"""
    db.session.execute(sql, {"message_id": message_id})
    db.session.commit()


def get_message(message_id):
    sql = """SELECT messages.id AS id, users.username AS username, users.id AS user_id,
                    messages.created_at AS created_at, content, messages.visible AS visible
             FROM messages
             LEFT JOIN users
                    ON user_id = users.id
             WHERE messages.id = :message_id"""
    message = db.session.execute(sql, {"message_id": message_id}).fetchone()
    return message
