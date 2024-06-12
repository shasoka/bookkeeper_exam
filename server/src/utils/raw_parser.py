import json
import re

ROOT_DIR = "../../"


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
    bad_lines = []
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
        elif line.startswith("Тема"):
            if is_toc(line) and line not in questions_dict[cur_section].keys():
                questions_dict[cur_section][line] = dict()
            if not is_toc(line):
                cur_theme = get_full_theme(line, questions_dict[cur_section].keys())
        elif startswith_regex(line, r'^\d+\.'):
            questions_dict[cur_section][cur_theme][line] = {'correct': '', 'variants': []}
            cur_question = line
        elif startswith_regex(line, r'^[а-я]\)'):
            questions_dict[cur_section][cur_theme][cur_question]['variants'].append(line)
        else:
            bad_lines.append(line)

    [print(entry) for entry in set(bad_lines)]
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


def save_to_json(data, path):
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    # Заполнение словаря вопросов
    raw_lines = get_raw_data(ROOT_DIR + "resources/raw.txt")
    questions_dict = parse_questions(raw_lines)

    # Заполнение ответов на вопросы в имеющемся словаре
    answers_lines = get_raw_data(ROOT_DIR + "resources/answers.txt")
    questions_dict = parse_answers(questions_dict, answers_lines)

    # Сохранение в json
    save_to_json(questions_dict, ROOT_DIR + "out/data.json")
