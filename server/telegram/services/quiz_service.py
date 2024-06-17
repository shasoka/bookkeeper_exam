from aiogram import html


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


def parse_answers_from_poll(
        answers: list[str],
        option_ids: list[int]
) -> str:
    selected_answer = ""
    for i, ans in enumerate(answers):
        if i in option_ids:
            selected_answer += ans[0]
    return selected_answer
