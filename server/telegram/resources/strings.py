from typing import Final

from aiogram import html

from database.models import UserSession

SUCCESS_STATUSES: Final[list[str]] = [
    "Красава",
    "Молодец",
    "Хорошо",
    "Нормалдаки",
    "Вы прекрасны, уважаемый",
    "Все как у людей",
    "Отлично справляешься",
    "Потрясающе",
    "Так держать!",
    "Победа!",
    "Супер!",
    "Мастерски!",
    "Невероятно!",
    "Великолепно!",
    "Восхитительно!",
    "Наливай! НАЛИВАЙ!!!",
    "5 баллов в диплом",
    "Грандиозный результат",
]

FAIL_STATUSES: Final[list[str]] = [
    "Учись салага...",
    "Плаки-плаки)",
    "Ты че? Соберись, тут же все элементарно",
    "Мда, трэш.",
    "Затролен. Школьник.",
    "Я проанализировал ваш ответ. Вам следует вернуться на кухню.",
    "Было близко",
    "Наводчик контужен",
    "Броня не пробита",
    "Осечка",
    "Игра была равна, играли два говна...",
    "Штирлиц еще никогда прежде не был так близок к успеху...",
    "Ну, попытка засчитана",
    "Это 2 балла в диплом. Железобетонно.",
]

SUCCESS_EFFECT_IDS: Final[list[str]] = [
    "5104841245755180586",  # 🔥
    "5107584321108051014",  # 👍
    "5044134455711629726",  # ❤️
    "5046509860389126442",  # 🎉
]

FAIL_EFFECT_IDS: Final[list[str]] = [
    "5104858069142078462",  # 👎
    "5046589136895476101",  # 💩
]


# --- #


RESTART_COMMAND: Final[str] = "restart"
HEAL_COMMAND: Final[str] = "heal"
CHANGE_HINTS_POLICY_COMMAND: Final[str] = "change_hints_policy"


# --- #


NOT_AUTHORIZED = (
    "Плаки-плаки? 😭\n"
    "Бесплатный только хлеб в мышеловке, братуха\n"
    "Чтобы получить доступ, пиши сюда ➡️ @shasoka"
)
PET_ME: Final[str] = "🫳🐕"
SECTIONS_FROM_START: Final[str] = "Так уж и быть! Выбирай! 🐶❤️‍🔥"
SECTIONS_FROM_RESTART: Final[str] = "А ты хитер. Можешь не гладить, выбирай раздел 🫡"
FORWARD = "➡️"
BACK = "⬅️"
BACK_TO_SECTIONS = "◀️ К разделам"
BACK_TO_THEMES = "◀️ К темам"
MARK_THEME = "🟢 Пометить тему"
LETS_GO = "▶️ Начать с первого ▶️"
LETS_SHUFFLE = "🔀 Начать вперемешку 🔀"
HINT = "Подсказать?.. 🤫"
NO_MORE_HINTS = "Дальше сам 😶"
SOMETHING_WENT_WRONG = (
    "🫠 Что-то пошло не так.\n🔴 Вероятно, у тебя нет активной сессии или ты прорешал все вопросы в ней."
)
HEAL_ALERT = "⚠️\nЕсли Саймон не проверяет твой ответ, или возникают прочие ошибки - попробуй воспользоваться командой /heal, чтобы восстановить сломанную сессию, или /restart, чтобы начать новую сессию"
COULDNT_DELETE_MSG = "❌🧹 Я не смог удалить сообщение %s.\n\n❕🔧 Если ты видишь это оповещение, советую прописать /heal, и, пожалуйста, напиши @shasoka!\nЕму очень интересно, как ты смог меня сломать 🤕"
HINTS_ON = "🌞 Подсказки включены"
HINTS_OFF = "🌑 Подсказки выключены"


# --- #


def on_start_msg(full_name: str) -> str:
    return f"""Привет 👋, {html.bold(full_name)}!
        \nМеня зовут {html.bold('Саймон')} и я ... {html.spoiler(html.italic('косоглазый 👀'))}, но это не помешает мне проверить твои знания по бухучету.
        \n☑️ Я приготовил для тебя {html.code('1061')} {html.bold('тестовое')} задание (у меня {html.bold('нет')} заданий с установкой порядка или соответсивия, а также вставкой слов), которые разбиты на {html.code('31')} тему и {html.code('3')} раздела:
        \n1. {html.bold('Теория бухучета')}\n2. {html.bold('Бухгалтерский (финансовый) учет')}\n3. {html.bold('ФЗ "О бухгалтерсом учете", ПБУ')}
        \nЯ умею отслеживать твои результаты в пределах выбранной темы, чтобы после завершения теста ты мог прорешать заново те вопросы, на которых облажался.
        \nРади собственного удобства ты можешь периодически очищать чат со мной. Сам я этого делать не умею, увы... Средства, которыми я реализован, не позволяют мне очищать чат полностью. Но под каждым сообщением, которое я не сумею удалить сам будет кнопка - 🗑 - для его быстрогого удаления.
        \nДля того, чтобы выйти из выбранной темы, напиши /restart, или выбери эту команду в {html.code('Меню')}, но учти, что я забуду твой прогресс в покинутой теме!\nКоманда /start запустит меня с самого начала, так что советую пользоваться завершением сессии через /restart.
        \nПогладь меня, пожалуйста, и я пущу тебя к вопросам...\n\n\n🥺👇
        """


def on_section_chosen(chosen_section: int) -> str:
    return f"👩‍🎓 Раздел {'I' * chosen_section}:"


def on_theme_chosen(title: str, questions_total: int) -> str:
    return f"""
        ⚰️ Ставки сделаны, ставок больше нет... или есть?
        \nВы выбрали {html.italic(title)}.
        \n❔ Вопросов в этой теме: {html.code(questions_total)}. 
        \nКнопки говорят сами за себя. Удачи.
        """


def on_quiz_end_fail(session: UserSession) -> str:
    return f"""
        Ты старался, держи чоколадку 🍫
        \nПравильных ответов: {html.code(str(session.questions_total - len(session.incorrect_questions)) + '/' + str(session.questions_total))}
        \nЯ запомнил вопросы, в которых ты ошибся. Если хочешь перерешать их, жми на кнопку - 🧩 - внизу ({html.italic('вопросы будут следовать в том порядке, в котором они встречались тебе в тесте')}).
        \nЕсли желаешь вернуться к выбору раздела и темы, пиши /restart ♻️
        """


def on_quiz_end_success(session: UserSession) -> str:
    return f"""
        Мои поздравления, держи целых две чоколадки. Вот тебе первая 🍫 и вторая 🍫
        \nПравильных ответов: {html.code(str(session.questions_total - len(session.incorrect_questions)) + '/' + str(session.questions_total))}
        \nТы - живая легенда. Горжусь 🏅
        \nЕсли желаешь вернуться к выбору раздела и темы, пиши /restart ♻️
        """
