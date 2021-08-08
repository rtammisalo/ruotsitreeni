from db import db


def get_last_messages(message_count):
    sql = " ".join(("SELECT users.username as username, created_at, content",
                    "FROM messages",
                    "LEFT JOIN users ON user_id = users.id",
                    "ORDER BY created_at DESC",
                    "LIMIT :message_count"))
    messages = db.session.execute(
        sql, {"message_count": message_count}).fetchall()
    messages.reverse()

    return messages


def add_message(user_id, message):
    sql = " ".join(("INSERT INTO messages (user_id, created_at, content)",
                    "VALUES (:user_id, NOW(), :content)"))
    db.session.execute(sql, {"user_id": user_id, "content": message})
    db.session.commit()
