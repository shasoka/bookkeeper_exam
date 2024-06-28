"""Module, that stores string constants."""


from enum import StrEnum, Enum
from typing import Final

from aiogram import html


class NavButtons(StrEnum):
    """Enum class with strings for navigation buttons."""

    # Simple buttons
    BACK_ARROW: Final[str] = "⬅️"
    BACK_TRIANGLE: Final[str] = "◀️"
    FORWARD_ARROW: Final[str] = "➡️"
    FORWARF_TRIANGLE: Final[str] = "▶️"
    FINISH: Final[str] = "🏁"

    # Buttons with legend
    BACK_TO_SECTIONS: Final[str] = "◀️ К разделам"
    BACK_TO_THEMES: Final[str] = "◀️ К темам"
    LETS_GO: Final[str] = "▶️ Начать с первого ▶️"
    LETS_SHUFFLE: Final[str] = "🔀 Начать вперемешку 🔀"


class MiscButtons(StrEnum):
    """Enum class with strings for different not grouped buttons."""

    # Button for marking the chosen theme as "done_full"
    MARK_THEME: Final[str] = "🟢 Пометить тему"

    # Button for showing hint
    HINT: Final[str] = "Подсказать?.. 🤫"

    # Button to go to the sections after /start
    PET_ME: Final[str] = "🫳🐕"

    # Delete message button
    DELETE: Final[str] = "🗑"

    # Start exam button
    FIGHT_ME: Final[str] = "⚔️"

    # Button for quiz_incorrect callback
    PUZZLE: Final[str] = "🧩"


class Markers(StrEnum):
    """Enum class with strings for theme markers."""

    GREEN: Final[str] = "🟢"
    YELLOW: Final[str] = "🟡"
    ORANGE: Final[str] = "🟠"
    RED: Final[str] = "🔴"


class SlashCommands(StrEnum):
    """Enum class with strings for commands (like ``/start``)."""

    # Command for starting the exam session
    EXAM: Final[str] = "exam"

    # Message for restarting the quiz session
    RESTART: Final[str] = "restart"

    # Message for restoring the user session's (exam or quiz) messages and progress if any exists
    HEAL: Final[str] = "heal"

    # Command for changing hints policy
    HINTS_POLICY: Final[str] = "change_hints_policy"


class Messages(StrEnum):
    """Enum class with strings for messages, which bot sends to user."""

    # Tick
    TICK: Final[str] = "✅"

    # Cross
    CROSS: Final[str] = "❌"

    # Message for unauthorized users
    NOT_AUTHORIZED: Final[str] = (
        "Плаки-плаки? 😭\nБесплатный только хлеб в мышеловке, братуха\nЧтобы получить доступ, пиши сюда ➡️ @shasoka"
    )

    # Message after the "pet_me_button" pressed
    SECTIONS_FROM_START: Final[str] = "Так уж и быть! Выбирай! 🐶❤️‍🔥"

    #  Message after the /restart entered
    SECTIONS_FROM_RESTART: Final[str] = (
        "А ты хитер. Можешь не гладить, выбирай раздел 🫡"
    )

    # Message after the certain section was chosen
    ON_SECTIONS_CHOSEN: Final[str] = "👩‍🎓 Раздел %s:"
    ONE: Final[str] = "I"

    # Message after the certain theme was chosen
    ON_THEME_CHOSEN: Final[str] = (
        "⚰️ Ставки сделаны, ставок больше нет... или есть?\nВы выбрали %s.\n❔ Вопросов в этой теме: %s. \nКнопки говорят сами за себя. Удачи."
    )

    # Message after the /heal entered and nothing to restore was found
    SOMETHING_WENT_WRONG = "🫠 Что-то пошло не так.\n🔴 Вероятно, у тебя нет активной сессии или ты прорешал все вопросы в ней."

    # Message which occurs if bot couldn't delete certain message
    COULDNT_DELETE_MSG = "❌🧹 Я не смог удалить сообщение %s. Вероятно, оно уже было удалено.\n\n❕🔧 Если ты видишь это оповещение, советую прописать /heal.\n"

    # Messages for switching on and off the hints
    HINTS_ON = "🌞 Подсказки включены"  # On
    HINTS_OFF = "🌑 Подсказки выключены"  # Off

    # Message which occurs if bot couldn't add effect to certain message
    INVALID_EFFECT_ID = (
        f"\n\n⚠️🔇Не смог добавить эффект %s к сообщению. Сообщи об этом @shasoka."
    )

    # Message after the /exam entered
    EXAM_MESSAGE = f"""Ты все-таки {html.bold('решился')}, бухгалтер?.. 🥷🏼
                   \nВ режиме экзамена ты сможешь доказать мне, что достоин. {html.spoiler('Достоин чего? Не знаю. Я просто нагоняю пафоса 🌡')}
                   \nЯ подберу для тебя {html.code('35')} случайных вопросов из всей моей коллекции 🗄 и дам на их решение {html.code('20')} минут ⏰
                   \n⚠️ {html.bold('Подсказки во время экзамена будут недоступны!')}
                   \n\nТвоя главная задача - {html.italic('не опозориться')}, ой, то есть {html.italic('решить как можно больше вопросов и допустить как можно меньше ошибок')}.
                   \n\nТвой наилучший результат: %s{html.code('/35')} 🏆 
                   \n\nНу, что? Готов? {html.spoiler('Хватай клинок 🗡 Будем драться 🤼')} 
                   """
    THIS_IS_EXAM: Final[str] = html.code("Это экзамен, братуха 🥶")  # Header for each exam question

    # Message after the /start entered
    ON_START_MESSAGE: Final[str] = f"""Привет 👋, %s!
        \nМеня зовут {html.bold('Саймон')} и я ... {html.spoiler(html.italic('косоглазый 👀'))}, но это не помешает мне проверить твои знания по бухучету.
        \n☑️ Я приготовил для тебя {html.code('1061')} {html.bold('тестовое')} задание (у меня {html.bold('нет')} заданий с установкой порядка или соответсивия, а также вставкой слов), которые разбиты на {html.code('31')} тему и {html.code('3')} раздела:
        \n1. {html.bold('Теория бухучета')}\n2. {html.bold('Бухгалтерский (финансовый) учет')}\n3. {html.bold('ФЗ "О бухгалтерсом учете", ПБУ')}
        \nЯ умею отслеживать твои результаты в пределах выбранной темы, чтобы после завершения теста ты мог прорешать заново те вопросы, на которых облажался.
        \nРади собственного удобства ты можешь периодически очищать чат со мной. Сам я этого делать не умею, увы... Средства, которыми я реализован, не позволяют мне очищать чат полностью. Но под каждым сообщением, которое я не сумею удалить сам будет кнопка - 🗑 - для его быстрогого удаления.
        \nДля того, чтобы выйти из выбранной темы, напиши /restart, или выбери эту команду в {html.code('Меню')}, но учти, что я забуду твой прогресс в покинутой теме!\nКоманда /start запустит меня с самого начала, так что советую пользоваться завершением сессии через /restart.
        \nПогладь меня, пожалуйста, и я пущу тебя к вопросам...\n\n\n🥺👇
        """

    # Message after the exam session end
    ON_EXAM_END: Final[str] = f"""
        Ладно, ладно. Успокойся. Финиш 🏁
        \n%s Правильных ответов: %s{html.code('/35')}
        \n\nКаков бы ни был результат, помни, что ты - легенда 👑
        \n\nВторой попытки не будет. Сам понимаешь, это все-таки {html.bold('ЭКЗАМЕН')}, тут головой думать надо! 🧠
        """
    EXAM_RECORD: Final[str] = (
        "Так уж и быть, обрадую. Ты побил свой предыдущий рекорд! ✳️"
    )  # Part of exam summary message with congratulations
    EXAM_NOT_RECORD: Final[str] = (
        "Даже лучшие порой ошибаются... Но это тоже хороший результат! *️⃣"
    )  # Neutral part of exam summary message
    TIMES_UP: Final[str] = html.code("[ВРЕМЯ ВЫШЛО]")  # Header for exam summary message if time's up

    # Fail summary message for quiz session end
    ON_QUIZ_END_FAIL: Final[str] = f"""
        Ты старался, держи чоколадку 🍫
        \nПравильных ответов: %s
        \nЯ запомнил вопросы, в которых ты ошибся. Если хочешь перерешать их, жми на кнопку - 🧩 - внизу ({html.italic('вопросы будут следовать в том порядке, в котором они встречались тебе в тесте')}).
        \nЕсли желаешь вернуться к выбору раздела и темы, пиши /restart ♻️
        """

    # Success summary message for quiz session end
    ON_QUIZ_END_SUCCESS: Final[
        str
    ] = f"""
        Мои поздравления, держи целых две чоколадки. Вот тебе первая 🍫 и вторая 🍫
        \nПравильных ответов: %s
        \nТы - живая легенда. Горжусь 🏅
        \nЕсли желаешь вернуться к выбору раздела и темы, пиши /restart ♻️
        """

    # Part of incorrect answer message with correct variants
    CORRECT_ANSWER: Final[str] = "\n\n❕ " + html.bold("Правильный ответ:") + " "

    # Poll headers
    SELECT_ONE: Final[str] = "Выбери верный ответ"
    SELECT_MANY: Final[str] = "Выбери верные ответы"


class CallbackQueryAnswers(StrEnum):
    """Enum class with strings for in-chat notifications."""

    # Answer which occurs if bot is creating new session and clearing old ones
    SESSION_CREATION_DELAY: Final[str] = "♻️ Чищу сесии | %s"
    EXAM_DELAY: Final[str] = "Запускаю таймер! ⏳"
    QUIZ_DELAY: Final[str] = "Создаю для тебя новую! 📒"

    # Answer which occurs if new quiz session created successfully without clearing old ones
    QUIZ_SESSION_CREATED: Final[str] = "✅ Сессия создана"

    # Answer which occurs if new exam session created successfully without clearing old ones
    EXAM_SESSION_CREATED: Final[str] = "⏳ Время пошло"
    TIMER: Final[str] = "⏳"

    # Answer which occurs if theme marked successfully
    THEME_MARKED: Final[str] = "✅ Тема помечена"


class Alerts(StrEnum):
    """Enum class with strings for alert dialogs."""

    # Part of the alert which occurs when hint was requested
    NO_MORE_HINTS = "Дальше сам 😶"

    # Alert which occurs every 10 session creations
    HEAL_ALERT = "⚠️ Если Саймон не проверяет твой ответ, или возникают прочие ошибки - попробуй воспользоваться командой /heal, чтобы восстановить сломанную сессию, или /restart, чтобы начать новую."


class Arrays(Enum):
    """Enum class with lists of miscellaneous strings."""

    # Congratulations on correct answers
    SUCCESS_STATUSES: Final[list[str]] = [
        "Напомню: ты - живая легенда",
        "Будь счастлив, здоров, хорошего дня.",
        "Хорош, бухгалтер",
        "Нормалдаки",
        "Вы прекрасны, уважаемый",
        "Все как у людей",
        "Отлично справляешься",
        "Умопомрачительно!",
        "Так держать! Делай как делаешь.",
        "Победа!",
        "Ошеломительно, коллега.",
        "Я проанализиорвал ваш ответ. Можете не возвращаться на кухню.",
        "С Новым Годом!",
        "Сегодня праздник у девчат!",
        "Дело в шляпе. Или как там?.. Короче, в шляпе.",
        "Наливай! НАЛИВАЙ!!!",
        "5 баллов в диплом",
        "Грандиозный результат",
    ]

    # Trolling on incorrect answers
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

    # Success effect ids
    SUCCESS_EFFECT_IDS: Final[list[str]] = [
        "5104841245755180586",  # 🔥
        "5107584321108051014",  # 👍
        "5159385139981059251",  # ❤️
        "5046509860389126442",  # 🎉
    ]

    # Fail effect ids
    FAIL_EFFECT_IDS: Final[list[str]] = [
        "5104858069142078462",  # 👎
        "5046589136895476101",  # 💩
    ]

    # Changelogs
    # Were used during the release of functional updates to notify active users about innovations
    # or bug-fixes
    CHANGELOGS: Final[list[str]] = [
        # 20.06.2024
        f"""{html.code('[UPDATE CHANGELOG 20.06.2024]')}
        \nДля тебя ничего не изменилось, но изнутри я заметно похорошел 💅
        \n\n⚠️ Послание для тех, кто не пользовался мной несколько дней: Телеграм не даст удалить мне некоторые ваши старые сообщения, поэтому, если получите сообщение об ошибке ❌🧹, воспользуйтесь командой /heal. 
        \n\nКак обычно, если что-то сломается, пиши @shasoka
        \nМожешь спокойно удалять это сообщение 🫥
        \nУспехов! 🤞
        """,
        # 21.06.2024
        f"""{html.code('[UPDATE CHANGELOG 21.06.2024]')}
        \n🎲 {html.italic(html.bold('Игра была равна, играли два... игрока: @shasoka и TelegramBotAPI'))}.
        \n\n💊 Сперва о том, что, вероятно, заставляло тебя в первой половине вчерашнего дня пользоваться командой /heal.
        \n{html.code('31.05.2024')} Телеграм обрадовал пользователей и разработчиков добавлением возможности отправки сообщений с анимациями, вроде тех, что ты уже встречал в процессе решения теста. Новая функция! Вау, звучит круто, но тогда почему Телеграм один из участников вышеупомянутой игры? Потому что забыл обновить соответствующую документацию для разработчиков и отправил их самих изучать, как эти самые анимации должны работать. И все бы ничего, вот только вчерашним утром кто-то в команде разработки Телеграма решил, что анимация для эффекта с сердечком ❤️ теперь будет иметь новый идентификатор, который не давал мне отправлять тебе сообщения с результатами проверки твоего ответа. Если интересно узнать обо всей этой суете подробнее - {html.link('вот', "https://stackoverflow.com/a/78645950/18955009")}, пожалуйста.
        \nТеперь, в случае неудачи отправки сообщения с анимацией, ты будешь получать сообщение без нее, но со строкой-уведомлением ⚠️🔇 о том, какая из анимаций сломалась.
        \n\nТеперь о хорошем 🫂 
        \n1. 🪲 Исправлена некритичная ошибка ведения отладочной информации.
        \n2. 🤫 В очередной раз переработы подсказки. Теперь подсказки будут показывать тебе не просто один верный ответ. Количество ответов, которые выдаст подсказка, теперь вычисляется по формуле {html.code('(КОЛИЧЕСТВО ВЕРНЫХ ОТВЕТОВ / 2)')}, округление работает в сторону ближайшего меньшего целого ({html.italic('*если в вопросе три правильных ответа, подсказка выдаст тебе только одну из трех правильных букв')}).
        \n3. 🚦 Переработаны маркеры тем. Добавлен новый маркер и изменены правила окраски:
        \n{html.code('🔴 - Ни разу не запущенная тема')}\n{html.code('🟠 - Хотя бы раз запущенная тема')}\n{html.code('🟡 - Тема, пройденная с ошибками')}\n{html.code('🟢 - Тема, пройденная без ошибок')}
        \n\n⚠️ Тем, кто не пользовался мной несколько дней, напоминаю: Телеграм не даст удалить мне некоторые старые сообщения, поэтому, если получите сообщение об ошибке ❌🧹, воспользуйтесь командой /heal.
        \nКак обычно, если что-то сломается, пиши @shasoka
        \nМожешь спокойно удалять это сообщение 🫥
        \nУспехов! 🤞""",
        # 22.06.2024
        f"""{html.code('[UPDATE CHANGELOG 22.06.2024]')}
        \n🆕 {html.bold('Печально, но, кажется, это последнее сообщение от моего разработчика... Тем не менее, представляю вам режим экзамена!')}
        \n\n🎓 Начать экзамен можно командой /exam. Я выберу для тебя 35 случайных вопросов и дам 20 минут на их решение. Все просто, но я старался! Надеюсь, ты оценишь.
        \n\n⚠️ Тем, кто не пользовался мной несколько дней, напоминаю: Телеграм не даст удалить мне некоторые старые сообщения, поэтому, если получите сообщение об ошибке ❌🧹, воспользуйтесь командой /heal.
        \nКак обычно, если что-то сломается, пиши @shasoka
        \nМожешь спокойно удалять это сообщение 🫥
        \nУспехов! 🤞""",
    ]
