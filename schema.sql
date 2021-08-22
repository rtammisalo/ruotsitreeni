CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    account_type INTEGER,
    created_at TIMESTAMP
);

CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    title TEXT UNIQUE,
    topic TEXT,
    created_at TIMESTAMP,
    visible BOOLEAN
);

CREATE TABLE words (
    id SERIAL PRIMARY KEY,
    exercise_id INTEGER REFERENCES exercises,
    finnish_word TEXT,
    swedish_word TEXT,
    image_data BYTEA
);

CREATE TABLE answer_choices (
    id SERIAL PRIMARY KEY,
    word_id INTEGER REFERENCES words,
    wrong_answer TEXT
);

CREATE TABLE answers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users ON DELETE CASCADE,
    word_id INTEGER REFERENCES words,
    result BOOLEAN
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users ON DELETE CASCADE,
    created_at TIMESTAMP,
    content TEXT,
    visible BOOLEAN
);
