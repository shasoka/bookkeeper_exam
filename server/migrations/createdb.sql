-- DROP DATABASE accounting_questions;
--
-- CREATE DATABASE accounting_questions;

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
    telegram_id TEXT,
    username TEXT,
    checked_update BOOLEAN DEFAULT false,
    hints_allowed BOOLEAN DEFAULT true,
    help_alert_counter INTEGER default 0,
    themes_tried integer[] default array []::integer[],
    themes_done_full integer[] default array []::integer[],
    themes_done_particular integer[] default array []::integer[]
);

CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP default NOW(),
    user_id INTEGER,
    theme_id INTEGER,
    questions_queue INTEGER[],
    progress INTEGER,
    incorrect_questions INTEGER[],
    questions_total INTEGER,
    hints INTEGER,
    hints_total INTEGER,
    cur_q_msg INTEGER default null,
    cur_p_msg INTEGER default null,
    cur_a_msg INTEGER default null,
    cur_s_msg INTEGER default null,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (theme_id) REFERENCES themes(id)
);

INSERT INTO users (telegram_id) VALUES ('401791628'),
                                       ('760058245'),
                                       ('768653895'),
                                       ('1005587901'),
                                       ('5258574541'),
                                       ('620396347'),
                                       ('1098632718'),
                                       ('5428878153'),
                                       ('1043969446'),
                                       ('518027491'),
                                       ('701161572');
