"""Module for utility functions."""

from aiogram import html

from enums.literals import TRANSLITERATE_DICT


def transliterate(text: str) -> str:
    """
    Function, which transliterates text from Russian into English using transliterate dictionary.

    :param text: source string to transliterate
    :return: transliterated string
    """

    translit_text: str = ""
    for char in text:
        translit_text += TRANSLITERATE_DICT.get(char, char)
    return translit_text


def parse_answers_from_question(raw_answers: list[str]) -> tuple[list[str], str]:
    """
    Function, which parses ``answers`` from ``Question`` object.

    :param raw_answers: a list of raw ``answers`` from ``Question`` object
    :return: a list of parsed and formatted answers and a string of all answers
    """

    answers: list = []
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
    """
    Function, which parses selected ``option_ids`` from ``PollAnswer`` object.

    :param answers: a list of chosen poll ``option_ids`` by user
    :param option_ids: a list of poll ``option_ids``
    :return: formatted string consisting of selected answers
    """

    selected_answer: str = ""
    for i, ans in enumerate(answers):
        if i in option_ids:
            selected_answer += ans[0]
    return selected_answer
