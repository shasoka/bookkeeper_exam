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
