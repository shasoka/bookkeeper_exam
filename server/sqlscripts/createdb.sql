DROP DATABASE accounting_questions;

CREATE DATABASE accounting_questions;

CREATE TABLE sections (
    id SERIAL PRIMARY KEY,
    title TEXT
);

CREATE TABLE themes (
    id SERIAL PRIMARY KEY,
    section_id INTEGER,
    title TEXT,
    FOREIGN KEY (section_id) REFERENCES sections(id)
);

CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    theme_id INTEGER,
    title TEXT,
    answers TEXT[],
    correct_answer TEXT,
    FOREIGN KEY (theme_id) REFERENCES themes(id)
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id TEXT
);

CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    theme_id INTEGER,
    questions_queue INTEGER[],
    progress INTEGER,
    incorrect_questions INTEGER[],
    cur_q_msg INTEGER default null,
    cur_p_msg INTEGER default null,
    cur_a_msg INTEGER default null,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (theme_id) REFERENCES themes(id)
);

INSERT INTO users (telegram_id) VALUES ('401791628');
INSERT INTO users (telegram_id) VALUES ('760058245');
