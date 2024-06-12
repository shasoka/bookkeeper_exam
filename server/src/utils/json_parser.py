import json
import os
import re

import psycopg2
from dotenv import load_dotenv

ROOT_DIR = "../../"

load_dotenv(ROOT_DIR + ".env")

# Константы конфигурации для соединения с БД
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")


def connect():
    try:
        with psycopg2.connect(user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT, dbname=DB_NAME) as conn:
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)


def get_raw_data(src):
    with open(src, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]
    return lines


def is_toc(theme: str) -> bool:
    pattern = r"^(Тема \d+)\.\s*(.*)$"
    match = re.match(pattern, theme)
    if match:
        return True
    else:
        return False


def get_full_theme(short_theme: str, toc: dict.keys) -> str:
    for title in toc:
        if short_theme in title:
            return title


def startswith_regex(line, pattern):
    regex = re.compile(pattern)
    return regex.match(line) is not None


# noinspection PyUnboundLocalVariable
def parse_questions(lines):
    questions_dict = dict()
    for line in lines:
        # В строке могут встречаться:
        #   а) Номера разделов
        #   б) Номера и названия тем в разделах
        #   в) Тип следующих далее вопросов
        #   г) Тип следующих далее вопросов
        #   д) Номер и формулировка вопроса
        #   д) Вариант ответа

        # Обработка разделов
        if line.startswith("Раздел"):
            if line not in questions_dict.keys():
                questions_dict[line] = dict()
                cur_section = line
        if line.startswith("Тема"):
            if is_toc(line) and line not in questions_dict[cur_section].keys():
                questions_dict[cur_section][line] = dict()
            if not is_toc(line):
                cur_theme = get_full_theme(line, questions_dict[cur_section].keys())
        if startswith_regex(line, r'^\d+\.'):
            questions_dict[cur_section][cur_theme][line] = {'correct': '', 'variants': []}
            cur_question = line
        if startswith_regex(line, r'^[а-я]\)'):
            questions_dict[cur_section][cur_theme][cur_question]['variants'].append(line)
    return questions_dict


# noinspection PyUnboundLocalVariable
def parse_answers(questions_dict: dict, answers_lines: list):
    for line in answers_lines:
        if line.startswith("Раздел"):
            cur_section = line
        if line.startswith("Тема"):
            cur_theme = line
        if startswith_regex(line, r'^\d+\.'):
            for question in questions_dict[cur_section][cur_theme].keys():
                if question.startswith(line[:line.index(".") + 1]):
                    questions_dict[cur_section][cur_theme][question]['correct'] = line[line.index(".") + 2:].lower()

    return questions_dict


def write_to_db(questions_dict: dict):
    connection = connect()

    with connection.cursor() as cursor:
        for section, themes in questions_dict.items():
            cursor.execute(f"INSERT INTO sections (title) VALUES ('{section}')")
            for theme_title, questions in themes.items():
                cursor.execute(
                    f"INSERT INTO themes (section_id, title) VALUES"
                    f"  ("
                    f"      (SELECT id FROM sections WHERE title = '{section}'),"
                    f"      '{theme_title}'"
                    f"  )"
                )
                for question, answers in questions.items():
                    variants = "{" + json.dumps(answers["variants"], ensure_ascii=False)[1:-1] + "}"
                    correct = answers["correct"]
                    cursor.execute(
                        f"INSERT INTO questions (theme_id, title, answers, correct_answer) VALUES"
                        f"  ("
                        f"      (SELECT id FROM themes WHERE title = '{theme_title}'),"
                        f"      '{question}',"
                        f"      '{variants}',"
                        f"      '{correct}'"
                        f"  )"
                    )
    connection.commit()
    connection.close()


if __name__ == "__main__":
    # Заполнение словаря вопросов
    raw_lines = get_raw_data(ROOT_DIR + "resources/raw.txt")
    questions_dict = parse_questions(raw_lines)

    # Заполнение ответов на вопросы в имеющемся словаре
    answers_lines = get_raw_data(ROOT_DIR + "resources/answers.txt")
    questions_dict = parse_answers(questions_dict, answers_lines)

    write_to_db(questions_dict)
