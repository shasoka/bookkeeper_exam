"""Module for CRUD functions."""

import math
import random
from typing import Literal

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload

from database.connection import SessionLocal
from database.models import User, UserSession, Theme, Question, Section
from enums.logs import Logs
from loggers.setup import LOGGER
from services.utility_service import parse_answers_from_question


# noinspection PyTypeChecker
async def get_user(telegram_id: str) -> User:
    """
    Function, that returns ``User`` object from DB by specified ``telegram_id``.

    :param telegram_id: string with user's unique Telegram id
    :return: matching ``User`` object
    """

    async with SessionLocal() as session:
        user = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return user.scalars().first()


# noinspection PyTypeChecker
async def changelog_seen(telegram_id: str) -> None:
    """
    Function, that sets user's ``changelog_seen`` field to True.

    :param telegram_id: string with user's unique Telegram id
    """

    async with SessionLocal() as session:
        user = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user.scalars().first()
        user.checked_update = True
        await session.commit()
        await session.refresh(user)


# noinspection PyTypeChecker
async def set_username(telegram_id: str, username: str) -> None:
    """
    Function, that sets the user's ``username``, if it is not listed in the DB.

    :param telegram_id: string with user's unique Telegram id
    :param username: username, which will be set
    """

    async with SessionLocal() as session:
        user = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user.scalars().first()
        # Username starts from @
        user.username = "@" + username
        await session.commit()
        await session.refresh(user)


# noinspection PyTypeChecker
async def change_hints_policy(telegram_id: str) -> None:
    """
    Function, that switches user's ``hints_allowed`` field.

    :param telegram_id: string with user's unique Telegram id
    """

    async with SessionLocal() as session:
        user = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user.scalars().first()
        user.hints_allowed = not user.hints_allowed
        await session.commit()
        await session.refresh(user)


# noinspection PyTypeChecker
async def update_themes_progress(
    telegram_id: str, theme_id: int, success: bool | None
) -> None:
    """
    Function, that updates ``themes_done_full``, ``themes_done_particular`` and ``themes_tried`` fields in ``users``
    table.

    If theme must be set to any of these fields, it will be removed from others.

    :param telegram_id: string with user's unique Telegram id
    :param theme_id: integer theme's id in ``themes`` table
    :param success: boolean flag, which should be provided in case of ``theme_done_full``
    """

    async with SessionLocal() as session:
        user = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user.scalars().first()

        if theme_id in user.themes_done_full:
            return

        if isinstance(success, bool):
            if success:
                await session.execute(
                    update(User)
                    .where(User.telegram_id == telegram_id)
                    .values(
                        themes_done_full=func.array_append(
                            user.themes_done_full, theme_id
                        )
                    )
                )
                await session.execute(
                    update(User)
                    .where(User.telegram_id == telegram_id)
                    .values(
                        themes_done_particular=func.array_remove(
                            user.themes_done_particular, theme_id
                        )
                    )
                )
                await session.execute(
                    update(User)
                    .where(User.telegram_id == telegram_id)
                    .values(themes_tried=func.array_remove(user.themes_tried, theme_id))
                )
            else:
                if theme_id in user.themes_done_particular:
                    return
                await session.execute(
                    update(User)
                    .where(User.telegram_id == telegram_id)
                    .values(
                        themes_done_particular=func.array_append(
                            user.themes_done_particular, theme_id
                        )
                    )
                )
                await session.execute(
                    update(User)
                    .where(User.telegram_id == telegram_id)
                    .values(themes_tried=func.array_remove(user.themes_tried, theme_id))
                )
        else:
            await session.execute(
                update(User)
                .where(User.telegram_id == telegram_id)
                .values(themes_tried=func.array_append(user.themes_tried, theme_id))
            )
        await session.commit()
        await session.refresh(user)


# noinspection PyTypeChecker
async def get_user_with_session(telegram_id: str) -> User:
    """
    Function, that returns the ``User`` object with ``UserSession`` selectinloaded from DB by specified ``telegram_id``.

    :param telegram_id: string with user's unique Telegram id
    :return: matching ``User`` object
    """

    async with SessionLocal() as session:
        user = await session.execute(
            select(User)
            .where(User.telegram_id == telegram_id)
            .options(selectinload(User.session))
        )
        return user.scalars().first()


# noinspection PyTypeChecker
async def increase_help_alert_counter(telegram_id: str) -> None:
    """
    Function, that increases ``help_alert_counter``.

    If counter % 10 == 0 than the reminder about ``/heal`` command will be spawned.

    :param telegram_id: string with user's unique Telegram id
    """

    async with SessionLocal() as session:
        user = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user.scalars().first()
        user.help_alert_counter += 1
        await session.commit()
        await session.refresh(user)


async def clear_session(message: Message | CallbackQuery, bot: Bot) -> None:
    """
    Function, that deletes all messages wich are bound with current ``user.session`` and deletes corresponding line
    from DB.

    :param message: ``aiogram.types.Message`` or ``aiogram.types.CallbackQuery`` which triggered this function
    :param bot: instance of ``aiogram.Bot``
    """

    async with SessionLocal() as session:
        user = await get_user_with_session(str(message.from_user.id))
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
                        await bot.delete_message(
                            chat_id=(
                                message.chat.id
                                if isinstance(message, Message)
                                else message.message.chat.id
                            ),
                            message_id=msg,
                        )
                    except TelegramBadRequest:
                        pass

            await session.delete(user_session)
            await session.commit()


async def init_exam_session(telegram_id: str) -> bool:
    """
    Function, that creates new exam session for user with specified ``telegram_id``.

    - Questions for exam session are randomized;
    - There are always 35 questions;
    - At least 1 question from each theme and 4 fully randomed from remainder;
    - Each question has 4 or fewer variants of answer;
    - Hints are disabled;
    - Theme won't be specified for such session;
    - Suggestion to solve incorrects again won't appear after exam end.

    If there is existing session for this user, function return ``False`` and creation stops.
    Otherwise - proceeds the session creation and returns ``True``.

    :param telegram_id: string with user's unique Telegram id
    :return: ``False`` if session was not created, ``True`` otherwise
    """

    async with SessionLocal() as session:
        user = await get_user_with_session(telegram_id)
        if user.session is not None:
            return False

        # Get all themes with loaded questions relationship
        themes = await session.execute(
            select(Theme).options(selectinload(Theme.questions))
        )
        themes = themes.scalars().all()

        # List for storing randomized questions
        selected_questions = []

        # Select one question from each theme
        for theme in themes:
            if theme.questions:
                randomed_q = random.choice(theme.questions)
                if len(parse_answers_from_question(randomed_q.answers)[0]) <= 4:
                    selected_questions.append(randomed_q)

        # Select last four questions from remainder
        num_remaining_questions = 35 - len(selected_questions)
        if num_remaining_questions > 0:
            # Get all questions which are not selected
            all_questions = await session.execute(select(Question))
            all_questions = all_questions.scalars().all()
            remaining_questions = [
                q
                for q in all_questions
                if q not in selected_questions
                and len(parse_answers_from_question(q.answers)[0]) <= 4
            ]
            selected_questions.extend(
                random.sample(remaining_questions, num_remaining_questions)
            )

        # Shuffle the selected questions
        random.shuffle(selected_questions)

        # Create new exam session
        questions_queue = [q.id for q in selected_questions]
        new_session = UserSession(
            user_id=user.id,
            incorrect_questions=[],
            questions_queue=questions_queue,
            questions_total=35,
            hints=0,
            hints_total=0,
            progress=0,
        )
        session.add(new_session)
        await session.commit()
        await session.refresh(new_session)
        return True


# noinspection PyTypeChecker
async def update_user_exam_best(telegram_id: str, score: int) -> None:
    """
    Function, that updates user's ``exam_best`` field.

    If new result is fewer or equal to already stored, no change.

    :param telegram_id: string with user's unique Telegram id
    :param score: number of correct answers
    """

    async with SessionLocal() as session:
        user = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user.scalars().first()
        if score > user.exam_best:
            user.exam_best = score
            LOGGER.info(Logs.EXAM_RECORD % (user.telegram_id + "@" + user.username))
            await session.commit()
            await session.refresh(user)
        else:
            return


async def init_session(telegram_id: str, theme_id: int, shuffle: bool) -> bool:
    """
    Function, that creates new quiz session for user with specified ``telegram_id``.

    - Questions for quiz session can be randomized if ``shuffle==True``;
    - Questions are selected from specified theme;
    - Hints are allowed if user's ``hints_allowed`` field is ``True``;
    - Number of hints equals to ceiling value of ``questions_total/10``;
    - Suggestion to solve incorrects again will appear after exam end.

    If there is existing session for this user, function return ``False`` and creation stops.
    Otherwise - proceeds the session creation and returns ``True``.

    :param telegram_id: string with user's unique Telegram id
    :param theme_id: specified id of theme from ``themes`` table
    :param shuffle: flag for shuffling questions or not
    :return: ``False`` if session was not created, ``True`` otherwise
    """

    async with SessionLocal() as session:
        user = await get_user_with_session(telegram_id)
        if user.session is not None:
            return False

        questions, questions_total = await get_questions_with_len_by_theme(theme_id)

        if shuffle:
            random.shuffle(questions)

        new_session = UserSession(
            user_id=user.id,
            theme_id=theme_id,
            incorrect_questions=[],
            questions_queue=[q.id for q in questions],
            questions_total=questions_total,
            hints=math.ceil(questions_total / 10),
            hints_total=math.ceil(questions_total / 10),
            progress=0,
        )
        session.add(new_session)
        await session.commit()
        await session.refresh(new_session)
        return True


# noinspection PyTypeChecker
async def rerun_session(telegram_id: str) -> None:
    """
    Function, that updates session if user is trying to solve incorrect questions.

    - ``questions_queue`` list is being replaced by ``incorrect_questions`` list;
    - ``incorrect_questions`` list clears;
    - ``progress`` sets to zero;
    - ``hints`` is being re-calculated.

    :param telegram_id: string with user's unique Telegram id
    """

    async with SessionLocal() as session:
        user = await session.execute(
            select(User)
            .where(User.telegram_id == telegram_id)
            .options(selectinload(User.session))
        )
        user_session = user.scalars().first().session
        incorrects = user_session.incorrect_questions
        user_session.questions_queue = incorrects
        user_session.incorrect_questions = []
        user_session.progress = 0
        user_session.questions_total = len(user_session.questions_queue)
        user_session.hints = math.ceil(user_session.questions_total / 10)
        user_session.hints_total = math.ceil(user_session.questions_total / 10)
        await session.commit()
        await session.refresh(user_session)


# noinspection PyTypeChecker
async def decrease_hints(telegram_id: str) -> None:
    """
    Function, that decreases user's hints count for current session if hint was requested.

    :param telegram_id: string with user's unique Telegram id
    """

    async with SessionLocal() as session:
        user = await session.execute(
            select(User)
            .where(User.telegram_id == telegram_id)
            .options(selectinload(User.session))
        )
        user_session = user.scalars().first().session

        user_session.hints -= 1
        await session.commit()
        await session.refresh(user_session)


# noinspection PyTypeChecker
async def save_msg_id(
    telegram_id: str, msg_id: int | None, flag: Literal["q", "p", "a", "s"]
) -> None:
    """
    Function, that saves message ids for:

    - ``q_msg``: message with Question
    - ``p_msg``: message with Poll
    - ``a_msg``: message for user's Answer result
    - ``s_msg``: message for Summary after session end

    Saved ids are used to delete old question before sending next one.

    :param telegram_id: string with user's unique Telegram id
    :param msg_id: unique identifier of message to save
    :param flag: boolean flag which is pointing to what type of message will be saved
    """

    async with SessionLocal() as session:
        user = await session.execute(
            select(User)
            .where(User.telegram_id == telegram_id)
            .options(selectinload(User.session))
        )
        user = user.scalars().first()
        user_session = user.session

        if user_session is None:
            return

        match flag:
            case "q":
                user_session.cur_q_msg = msg_id
            case "p":
                user_session.cur_p_msg = msg_id
            case "a":
                user_session.cur_a_msg = msg_id
            case "s":
                user_session.cur_s_msg = msg_id
        await session.commit()


# noinspection PyTypeChecker
async def increase_progress(telegram_id: str) -> None:
    """
    Function, that increases user's progress in current session. This function must be called after user's answer
    validation.

    :param telegram_id: string with user's unique Telegram id
    """

    async with SessionLocal() as session:
        user = await session.execute(
            select(User)
            .where(User.telegram_id == telegram_id)
            .options(selectinload(User.session))
        )
        user_session = user.scalars().first().session
        user_session.progress += 1
        await session.commit()
        await session.refresh(user_session)


# noinspection PyTypeChecker
async def append_incorrects(telegram_id: str, cur_question_id: int) -> None:
    """
    Function, that adds new incorrect question to ``incorrect_questions`` array-field.

    :param telegram_id: string with user's unique Telegram id
    :param cur_question_id: identifier of question in ``questions`` table
    """

    async with SessionLocal() as session:
        user = await session.execute(
            select(User)
            .where(User.telegram_id == telegram_id)
            .options(selectinload(User.session))
        )
        user_session = user.scalars().first().session
        await session.execute(
            update(UserSession)
            .where(UserSession.id == user_session.id)
            .values(
                incorrect_questions=func.array_append(
                    user_session.incorrect_questions, cur_question_id
                )
            )
        )
        await session.commit()
        await session.refresh(user_session)


# noinspection PyTypeChecker
async def get_questions_with_len_by_theme(theme_id: int) -> tuple[list[Question], int]:
    """
    Function, that returns list of questions from specified theme and its length.

    :param theme_id: specified id of theme from ``themes`` table
    """

    async with SessionLocal() as session:
        questions = await session.execute(
            select(Question).where(Question.theme_id == theme_id).order_by(Question.id)
        )
        questions = questions.scalars().all()
        return questions, len(questions)


# noinspection PyTypeChecker
async def get_cur_question_with_count(telegram_id: str) -> tuple[Question, int]:
    """
    Function, that returns current user's question based on session ``progress`` field and value of ``questions_total``
    field.

    :param telegram_id: string with user's unique Telegram id
    :return: tuple of current question and total questions count
    """

    async with SessionLocal() as session:
        user = await get_user_with_session(telegram_id)
        cur_question = await session.execute(
            select(Question)
            .where(Question.id == user.session.questions_queue[user.session.progress])
            .options(selectinload(Question.theme))
        )
        cur_question = cur_question.scalars().first()
        return cur_question, len(user.session.questions_queue)


async def get_sections() -> list[Section]:
    """
    Function, that returns a list of ``Section`` objects.

    :return: list of all existing sections in DB
    """

    async with SessionLocal() as session:
        sections = await session.execute(select(Section))
        return sections.scalars().all()


# noinspection PyTypeChecker
async def get_themes_by_section(section_id: int) -> list[Theme]:
    """
    Function, that returns a list of themes which are bounf to specified ``section_id``

    :param section_id: identifier of section in ``sections`` table
    :return: list of all existing themes bounded with specified ``section_id``
    """

    async with SessionLocal() as session:
        themes = await session.execute(
            select(Theme).where(Theme.section_id == section_id)
        )
        return themes.scalars().all()


# noinspection PyTypeChecker
async def get_theme_by_id(theme_id: int) -> Theme:
    """
    Function, that returns the ``Theme`` obect based on it's identifier.

    :param theme_id: specified id of theme from ``themes`` table
    :return: ``Theme`` object
    """

    async with SessionLocal() as session:
        theme = await session.execute(select(Theme).where(Theme.id == theme_id))
        return theme.scalars().first()
