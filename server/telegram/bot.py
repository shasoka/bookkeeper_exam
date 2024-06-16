import asyncio
import logging
import random
import sys
from typing import Annotated, Callable, Any, Dict, Awaitable

from aiogram import Bot, Dispatcher, html, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    TelegramObject,
    PollAnswer, )
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from aiogram3_di import setup_di, Depends
from config import (
    TG_TOKEN as TOKEN,
    SUCCESS_STATUSES,
    FAIL_STATUSES,
    SUCCESS_EFFECT_IDS,
    FAIL_EFFECT_IDS,
)
from database.connection import get_async_session, SessionLocal
from database.models import User, Section, Theme, UserSession, Question

DELETE_INLINE_BUTTON = InlineKeyboardButton(text="🗑", callback_data="delete")

dp = Dispatcher()

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


class AuthMiddleware(BaseMiddleware):
    # noinspection PyTypeChecker
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:

        async with SessionLocal() as session:
            if event.from_user:
                user = await session.execute(
                    select(User).where(User.telegram_id == str(event.from_user.id))
                )
                if not user.first():
                    await session.commit()
                    return await auth_fail_handler(event)
                else:
                    await session.commit()
                    return await handler(event, data)


dp.message.outer_middleware(AuthMiddleware())


async def auth_fail_handler(event: TelegramObject):
    return await event.answer(
        """
        Плаки-плаки? 😭
        \nБесплатный только хлеб в мышеловке, братуха
        \nЧтобы получить доступ, пиши сюда ➡️ @shasoka
        """,
        disable_notification=True,
    )
    # return await event.answer(
    #     """
    #     Технические работы 😭
    #     """,
    #     disable_notification=True,
    # )


# noinspection PyTypeChecker
@dp.message(CommandStart())
async def command_start_handler(
    message: Message
) -> None:

    await clear_session(message)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🫳🐕", callback_data="pet")],
            [DELETE_INLINE_BUTTON],
        ]
    )

    await message.answer(
        f"""
        Привет 👋, {html.bold(message.from_user.full_name)}!
        \nМеня зовут {html.bold('Саймон')} и я ... {html.spoiler(html.italic('косоглазый 👀'))}, но это не помешает мне проверить твои знания по бухучету.
        \n☑️ Я приготовил для тебя {html.code('1061')} {html.bold('тестовое')} задание (у меня {html.bold('нет')} заданий с установкой порядка или соответсивия, а также вставкой слов), которые разбиты на {html.code('31')} тему и {html.code('3')} раздела:
        \n1. {html.bold('Теория бухучета')}\n2. {html.bold('Бухгалтерский (финансовый) учет')}\n3. {html.bold('ФЗ "О бухгалтерсом учете", ПБУ')}
        \nЯ умею отслеживать твои результаты в пределах выбранной темы, чтобы после завершения теста ты мог прорешать заново те вопросы, на которых облажался.
        \nРади собственного удобства ты можешь периодически очищать чат со мной. Сам я этого делать не умею, увы... Средства, которыми я реализован, не позволяют мне очищать чат полностью. Но под каждым сообщением, которое я не сумею удалить сам будет кнопка - 🗑 - для его быстрогого удаления.
        \nДля того, чтобы выйти из выбранной темы, напиши /restart, или выбери эту команду в {html.code('Меню')}, но учти, что я забуду твой прогресс в покинутой теме!\nКоманда /start запустит меня с самого начала, так что советую пользоваться завершением сессии через /restart.
        \nПогладь меня, пожалуйста, и я пущу тебя к вопросам...\n\n\n🥺👇
        """,
        reply_markup=keyboard,
        disable_notification=True,
    )


# noinspection PyTypeChecker
@dp.message(Command("restart"))
async def command_restart_handler(
    message: Message
):

    await clear_session(message)
    await pet_me_button_handler(callback_query=message)


# noinspection PyTypeChecker
async def clear_session(message: Message):
    async with SessionLocal() as session:
        user = await session.execute(
            select(User)
            .where(User.telegram_id == str(message.from_user.id))
            .options(selectinload(User.session))
        )
        user = user.scalars().first()
        user_session = user.session
        if user_session:
            for msg in [
                user_session.cur_q_msg,
                user_session.cur_p_msg,
                user_session.cur_a_msg,
                user_session.cur_s_msg,
            ]:
                if msg:
                    try:
                        await bot.delete_message(chat_id=message.chat.id, message_id=msg)
                    except TelegramBadRequest:
                        pass

            await session.delete(user_session)
            await session.commit()


async def pet_me_button_handler(
    callback_query: CallbackQuery | Message,
    session: Annotated[AsyncSession, Depends(get_async_session)] = None,
):

    di = True
    if not session:
        session = await get_async_session().asend(None)
        di = False
    sections = await session.execute(select(Section))
    sections = sections.scalars().all()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{sections[0].title}", callback_data="section_1"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{sections[1].title}", callback_data="section_2"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"{sections[2].title}", callback_data="section_3"
                )
            ],
            [DELETE_INLINE_BUTTON],
        ]
    )

    if isinstance(callback_query, CallbackQuery):
        previous_message = callback_query.message
        await bot.delete_message(
            chat_id=previous_message.chat.id, message_id=previous_message.message_id
        )
        await callback_query.message.answer(
            "Так уж и быть! Выбирай! 🐶❤️‍🔥",
            reply_markup=keyboard,
            disable_notification=True,
        )
    else:
        await bot.send_message(
            chat_id=callback_query.chat.id,
            text="А ты хитер. Можешь не гладить, выбирай раздел 🫡",
            reply_markup=keyboard,
            disable_notification=True,
        )

    if not di:
        await session.close()


# noinspection PyTypeChecker
async def select_section_handler(
    callback_query: CallbackQuery,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    chosen_section = (
        int(callback_query.data[-1])
        if callback_query.data.startswith("section")
        else int(callback_query.data[-1])
    )
    themes = await session.execute(
        select(Theme).where(Theme.section_id == chosen_section)
    )
    themes = themes.scalars().all()

    start_page = (
        1 if callback_query.data.startswith("section") else int(callback_query.data[-3])
    )
    per_page = 5
    start_index = (start_page - 1) * per_page
    end_index = start_page * per_page

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    for i, theme in enumerate(themes[start_index:end_index]):
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=theme.title,
                    callback_data=f"theme_{theme.id},{str(chosen_section)}",
                )
            ]
        )

    last_page = False
    if len(themes) > end_index:
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text="➡️",
                    callback_data=f"page_{start_page + 1},{str(chosen_section)}",
                )
            ]
        )
    else:
        last_page = True

    # Add previous page button if not on the first page
    if start_page > 1:
        if last_page:
            keyboard.inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text="⬅️",
                        callback_data=f"page_{start_page - 1},{str(chosen_section)}",
                    )
                ]
            )
        else:
            keyboard.inline_keyboard[-1].insert(
                0,
                InlineKeyboardButton(
                    text="⬅️",
                    callback_data=f"page_{start_page - 1},{str(chosen_section)}",
                ),
            )

    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(text="◀️ К разделам", callback_data="pet")]
    )
    keyboard.inline_keyboard.append([DELETE_INLINE_BUTTON])

    previous_message = callback_query.message
    await bot.delete_message(
        chat_id=previous_message.chat.id, message_id=previous_message.message_id
    )
    await callback_query.message.answer(
        f"👩‍🎓 Раздел {'I' * chosen_section}:",
        reply_markup=keyboard,
        disable_notification=True,
    )


# noinspection PyTypeChecker
async def select_theme_handler(
    callback_query: CallbackQuery,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    temp_parser = callback_query.data.split(",")
    temp_parser[0] = temp_parser[0].split("_")[1]
    chosen_theme_from_callback, choosen_section = temp_parser
    chosen_theme = await session.execute(
        select(Theme).where(Theme.id == int(chosen_theme_from_callback))
    )
    chosen_theme = chosen_theme.scalars().first()

    questions_total = await session.execute(
        select(Question.id).where(Question.theme_id == int(chosen_theme_from_callback))
    )
    questions_total = len(questions_total.scalars().all())

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="◀️ К темам", callback_data="section_" + choosen_section
                ),
                InlineKeyboardButton(
                    text="Ехала ▶️",
                    callback_data="quiz_init_" + chosen_theme_from_callback,
                ),
            ],
            [DELETE_INLINE_BUTTON],
        ]
    )

    previous_message = callback_query.message
    await bot.delete_message(
        chat_id=previous_message.chat.id, message_id=previous_message.message_id
    )
    await callback_query.message.answer(
        f"""
        ⚰️ Ставки сделаны, ставок больше нет... или есть?
        \nВы выбрали {html.italic(chosen_theme.title)}.
        \n❔ Вопросов в этой теме: {html.code(questions_total)}. 
        \nКнопки говорят сами за себя. Удачи.
        """,
        reply_markup=keyboard,
        disable_notification=True,
    )


# noinspection PyTypeChecker
async def answer_quiz_handler(
    callback_query: CallbackQuery,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    if callback_query.data.startswith("quiz_init"):
        theme_id = int(callback_query.data.split("_")[2])

        questions = await session.execute(
            select(Question).where(Question.theme_id == theme_id)
        )
        questions = questions.scalars().all()
        random.shuffle(questions)

        user = await session.execute(
            select(User).where(User.telegram_id == str(callback_query.from_user.id))
        )
        user = user.scalar()

        new_session = UserSession(
            user_id=user.id,
            theme_id=theme_id,
            incorrect_questions=[],
            questions_queue=[q.id for q in questions],
            progress=0,
        )
        session.add(new_session)
        await session.commit()
        await session.refresh(new_session)

    if callback_query.data.startswith("quiz_end"):
        user = await session.execute(
            select(User)
            .where(User.telegram_id == str(callback_query.from_user.id))
            .options(selectinload(User.session))
        )
        user = user.scalar()

        previous_message = callback_query.message
        await bot.delete_message(chat_id=previous_message.chat.id, message_id=previous_message.message_id)
        await bot.delete_message(chat_id=previous_message.chat.id, message_id=user.session.cur_p_msg)
        await bot.delete_message(chat_id=previous_message.chat.id, message_id=user.session.cur_q_msg)

        summary_text_fail = f"""
        Ты старался, держи чоколадку 🍫
        \nПравильных ответов: {html.code(str(len(user.session.questions_queue) - len(user.session.incorrect_questions)) + '/' + str(len(user.session.questions_queue)))}
        \nЯ запомнил вопросы, в которых ты ошибся. Если хочешь перерешать их, жми на кнопку - 🧩 - внизу.
        \nЕсли желаешь вернуться к выбору раздела и темы, пиши /restart ♻️
        """

        summary_text_success = f"""
        Мои поздравления, держи целых две чоколадки. Вот тебе первая 🍫 и вторая 🍫
        \nПравильных ответов: {html.code(str(len(user.session.questions_queue) - len(user.session.incorrect_questions)) + '/' + str(len(user.session.questions_queue)))}
        \nТы - живая легенда. Горжусь 🏅
        \nЕсли желаешь вернуться к выбору раздела и темы, пиши /restart ♻️
        """

        success = True if len(user.session.incorrect_questions) == 0 else False

        s_msg = await callback_query.message.answer(
            text=summary_text_success if success else summary_text_fail,
            reply_markup=(
                InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🧩", callback_data="quiz_incorrect"
                            )
                        ]
                    ]
                )
                if not success
                else None
            ),
            message_effect_id=random.choice(SUCCESS_EFFECT_IDS),
            disable_notification=True,
        )

        user.session.cur_s_msg = s_msg.message_id
        await session.commit()

        return

    if callback_query.data.startswith("quiz_incorrect"):
        user = await session.execute(
            select(User)
            .where(User.telegram_id == str(callback_query.from_user.id))
            .options(selectinload(User.session))
        )
        user = user.scalar()
        user_session = user.session

        incorrects = user_session.incorrect_questions
        random.shuffle(incorrects)
        user_session.questions_queue = incorrects
        user_session.incorrect_questions = []
        user_session.progress = 0
        await session.commit()

    user = await session.execute(
        select(User)
        .where(User.telegram_id == str(callback_query.from_user.id))
        .options(selectinload(User.session))
    )
    user = user.scalar()
    user_session = user.session

    cur_question = await session.execute(
        select(Question).where(
            Question.id == user_session.questions_queue[user_session.progress]
        )
    )
    cur_question = cur_question.scalar()

    questions_total = len(user_session.questions_queue)

    previous_message = callback_query.message
    await bot.delete_message(chat_id=previous_message.chat.id, message_id=previous_message.message_id)
    if not callback_query.data.startswith("quiz_init") and not callback_query.data.startswith("quiz_incorrect"):
        await bot.delete_message(chat_id=previous_message.chat.id, message_id=user.session.cur_p_msg)
        await bot.delete_message(chat_id=previous_message.chat.id, message_id=user.session.cur_q_msg)

    answers = []
    for i, ans in enumerate(cur_question.answers):
        cur_ans = -1
        if ans[1] == ')':
            ans.replace("\n", " ")
            answers.append(ans.lower())
            cur_ans += 1
        else:
            answers[cur_ans] += (', ' + ans.lower())
    answers.sort(key=lambda x: x[0])
    answers_str = html.italic("\n\n".join(answers))
    q_msg = await callback_query.message.answer(
        f"{html.code(f'{user.session.progress + 1} / {questions_total}')}\n\n{html.bold(cur_question.title)}\n\n{answers_str}",
        disable_notification=True,
    )

    p_msg = await callback_query.message.answer_poll(
        question=(
            f"Выбери {html.bold('верный')} ответ"
            if len(cur_question.correct_answer) == 1
            else f"Выбери {html.bold('верные')} ответы"
        ),
        options=[ans.lower()[:2] for ans in answers],
        type="regular",
        allows_multiple_answers=True,
        is_anonymous=False,
        disable_notification=True,
    )

    user.session.cur_q_msg = q_msg.message_id
    user.session.cur_p_msg = p_msg.message_id
    await session.commit()


# noinspection PyTypeChecker
@dp.poll_answer()
async def on_poll_answer(
    poll_answer: PollAnswer,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    user = await session.execute(
        select(User)
        .where(User.telegram_id == str(poll_answer.user.id))
        .options(selectinload(User.session))
    )
    user = user.scalar()
    user_session = user.session

    cur_question = await session.execute(
        select(Question).where(
            Question.id == user_session.questions_queue[user_session.progress]
        )
    )
    cur_question = cur_question.scalar()

    questions_total = len(user_session.questions_queue)

    answers = []
    for i, ans in enumerate(cur_question.answers):
        if ans[1] == ')':
            answers.append(ans[0].lower())
        else:
            continue
    answers.sort(key=lambda x: x[0])
    selected_answer = ""
    for i, ans in enumerate(answers):
        if i in poll_answer.option_ids:
            selected_answer += ans[0]

    correct_answer = cur_question.correct_answer

    if selected_answer == correct_answer:
        a_msg = await bot.send_message(
            user.telegram_id,
            "✅ " + html.bold(random.choice(SUCCESS_STATUSES)),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=(
                                "Далее"
                                if user_session.progress < questions_total - 1
                                else "Завершить"
                            ),
                            callback_data=(
                                "quiz"
                                if user_session.progress < questions_total - 1
                                else "quiz_end"
                            ),
                        )
                    ]
                ]
            ),
            message_effect_id=random.choice(SUCCESS_EFFECT_IDS),
            disable_notification=True,
        )
    else:
        a_msg = await bot.send_message(
            user.telegram_id,
            "❌ "
            + html.bold(random.choice(FAIL_STATUSES))
            + "\n\n❕ "
            + html.bold("Правильный ответ:")
            + " "
            + html.italic(correct_answer),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text=(
                                "Далее"
                                if user_session.progress < questions_total - 1
                                else "Завершить"
                            ),
                            callback_data=(
                                "quiz"
                                if user_session.progress < questions_total - 1
                                else "quiz_end"
                            ),
                        )
                    ]
                ]
            ),
            message_effect_id=random.choice(FAIL_EFFECT_IDS),
            disable_notification=True,
        )
        await session.execute(
            update(UserSession)
            .where(UserSession.id == user_session.id)
            .values(
                incorrect_questions=func.array_append(
                    user_session.incorrect_questions, cur_question.id
                )
            )
        )

    user_session.cur_a_msg = a_msg.message_id
    user_session.progress += 1
    await session.commit()


async def delete_msg_handler(
    callback_query: CallbackQuery,
):
    previous_message = callback_query.message
    await bot.delete_message(
        chat_id=previous_message.chat.id, message_id=previous_message.message_id
    )


dp.callback_query.register(pet_me_button_handler, lambda c: c.data == "pet")
dp.callback_query.register(select_theme_handler, lambda c: c.data.startswith("theme"))
dp.callback_query.register(answer_quiz_handler, lambda c: c.data.startswith("quiz"))
dp.callback_query.register(delete_msg_handler, lambda c: c.data == "delete")
dp.callback_query.register(
    select_section_handler,
    lambda c: c.data.startswith("section") or c.data.startswith("page"),
)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Логгер
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Инверсия зависимостей
    setup_di(dp)
    # Запуск бота
    asyncio.run(main())
