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

INSERT INTO users (telegram_id) VALUES ('401791628');
INSERT INTO users (telegram_id) VALUES ('760058245');
