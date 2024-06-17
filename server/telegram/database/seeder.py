import json
import os

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
        with psycopg2.connect(
            user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT, dbname=DB_NAME
        ) as conn:
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)


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
                    variants = (
                        "{"
                        + json.dumps(answers["variants"], ensure_ascii=False)[1:-1]
                        + "}"
                    )
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
    with open(ROOT_DIR + "resources/data.json", "r", encoding="utf-8") as file:
        data_dict = json.load(file)
    write_to_db(data_dict)
