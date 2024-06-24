import math
import random

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload

from database.connection import SessionLocal
from database.models import User, UserSession, Theme, Question, Section


# noinspection PyTypeChecker
async def get_user(telegram_id: str) -> User:
    async with SessionLocal() as session:
        user = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return user.scalars().first()


# noinspection PyTypeChecker
async def changelog_seen(telegram_id: str) -> None:
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
    async with SessionLocal() as session:
        user = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user.scalars().first()
        user.username = "@" + username
        await session.commit()
        await session.refresh(user)


# noinspection PyTypeChecker
async def change_hints_policy(telegram_id: str) -> None:
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
    async with SessionLocal() as session:
        user = await session.execute(
            select(User)
            .where(User.telegram_id == telegram_id)
            .options(selectinload(User.session))
        )
        return user.scalars().first()


# noinspection PyTypeChecker
async def increase_help_alert_counter(telegram_id: str) -> None:
    async with SessionLocal() as session:
        user = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user.scalars().first()
        user.help_alert_counter += 1
        await session.commit()
        await session.refresh(user)


# noinspection PyTypeChecker
async def clear_session(message: Message | CallbackQuery, bot: Bot) -> None:
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
                            chat_id=message.chat.id
                            if isinstance(message, Message)
                            else message.message.chat.id,
                            message_id=msg
                        )
                    except TelegramBadRequest:
                        pass

            await session.delete(user_session)
            await session.commit()


async def init_exam_session(telegram_id: str) -> bool:
    async with SessionLocal() as session:
        user = await get_user_with_session(telegram_id)
        if user.session is not None:
            return False

        questions_collection = await session.execute(select(Question))
        questions_collection = questions_collection.scalars().all()

        questions_queue = random.sample([q.id for q in questions_collection], 35)

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
    async with SessionLocal() as session:
        user = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user.scalars().first()
        if score > user.exam_best:
            user.exam_best = score
            await session.commit()
            await session.refresh(user)
        else:
            return


# noinspection PyTypeChecker
async def init_session(theme_id: int, telegram_id: str, shuffle: bool) -> bool:
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
async def save_msg_id(telegram_id: str, msg_id: int | None, flag: str) -> None:
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
    async with SessionLocal() as session:
        themes = await session.execute(
            select(Question).where(Question.theme_id == theme_id).order_by(Question.id)
        )
        themes = themes.scalars().all()
        return themes, len(themes)


# noinspection PyTypeChecker
async def get_cur_question_with_count(telegram_id: str) -> tuple[Question, int]:
    async with SessionLocal() as session:
        user = await get_user_with_session(telegram_id)
        cur_question = await session.execute(
            select(Question).where(
                Question.id == user.session.questions_queue[user.session.progress]
            )
        )
        cur_question = cur_question.scalars().first()
        return cur_question, len(user.session.questions_queue)


# noinspection PyTypeChecker
async def get_sections() -> list[Section]:
    async with SessionLocal() as session:
        sections = await session.execute(select(Section))
        return sections.scalars().all()


# noinspection PyTypeChecker
async def get_themes_by_section(section_id: int) -> list[Theme]:
    async with SessionLocal() as session:
        themes = await session.execute(
            select(Theme).where(Theme.section_id == section_id)
        )
        return themes.scalars().all()


# noinspection PyTypeChecker
async def get_theme_by_id(theme_id: int) -> Theme:
    async with SessionLocal() as session:
        theme = await session.execute(select(Theme).where(Theme.id == theme_id))
        return theme.scalars().first()
