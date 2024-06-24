from aiogram import html


def transliterate(text):
    translit_dict = {
        "А": "A",
        "Б": "B",
        "В": "V",
        "Г": "G",
        "Д": "D",
        "Е": "E",
        "Ё": "Yo",
        "Ж": "Zh",
        "З": "Z",
        "И": "I",
        "Й": "Y",
        "К": "K",
        "Л": "L",
        "М": "M",
        "Н": "N",
        "О": "O",
        "П": "P",
        "Р": "R",
        "С": "S",
        "Т": "T",
        "У": "U",
        "Ф": "F",
        "Х": "Kh",
        "Ц": "Ts",
        "Ч": "Ch",
        "Ш": "Sh",
        "Щ": "Shch",
        "Ы": "Y",
        "Э": "E",
        "Ю": "Yu",
        "Я": "Ya",
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "e",
        "ё": "yo",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "й": "y",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "kh",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "shch",
        "ы": "y",
        "э": "e",
        "ю": "yu",
        "я": "ya",
        "ъ": "",
        "ь": "",
    }

    translit_text = ""
    for char in text:
        translit_text += translit_dict.get(char, char)
    return translit_text


def parse_answers_from_question(raw_answers: list[str]) -> tuple[list[str], str]:
    answers = []
    for i, ans in enumerate(raw_answers):
        cur_ans = -1
        if ans[1] == ")":
            ans.replace("\n", " ")
            answers.append(ans.lower())
            cur_ans += 1
        else:
            answers[cur_ans] += ", " + ans.lower()
    answers.sort(key=lambda x: x[0])
    return answers, html.italic("\n\n".join(answers))


def parse_answers_from_poll(answers: list[str], option_ids: list[int]) -> str:
    selected_answer = ""
    for i, ans in enumerate(answers):
        if i in option_ids:
            selected_answer += ans[0]
    return selected_answer
