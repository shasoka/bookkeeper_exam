import asyncio
import logging
import sys
from typing import Annotated, Callable, Any, Dict, Awaitable

from aiogram import Bot, Dispatcher, html, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, TelegramObject
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aiogram3_di import setup_di, Depends
from config import TG_TOKEN as TOKEN
from database.connection import get_async_session
from database.models import User, Section, Theme

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

        session = await get_async_session().__anext__()

        if event.from_user:
            user = await session.execute(select(User).where(User.telegram_id == str(event.from_user.id)))
            if not user.one_or_none():
                return await auth_fail_handler(event)
            else:
                return await handler(event, data)


dp.message.outer_middleware(AuthMiddleware())


async def auth_fail_handler(event: TelegramObject):
    return await event.answer("Плаки-плаки? 😭\n\nБесплатный только хлеб в мышеловке, братуха\n\nЧтобы получить доступ, пиши сюда ➡️ @shasoka")


# noinspection PyTypeChecker
@dp.message(CommandStart())
async def command_start_handler(
        message: Message,
) -> None:
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🫳🐕", callback_data="pet")]
    ])

    await message.answer(
        f"""
        Привет 👋, {html.bold(message.from_user.full_name)}!
        \nМеня зовут {html.bold('Саймон')} и я ... {html.spoiler(html.italic('косоглазый 👀'))}, но это не помешает мне проверить твои знания по бухучету.
        \n☑️ Я приготовил для тебя {html.code('1576')} {html.bold('тестовых')} заданий (у меня {html.bold('нет')} заданий с установкой порядка или соответсивия, а также вставкой слов), которые разбиты на {html.code('41')} тему и {html.code('3')} раздела:
        \n1. {html.bold('Теория бухучета')}\n2. {html.bold('Бухгалтерский (финансовый) учет')}\n3. {html.bold('ФЗ "О бухгалтерсом учете", ПБУ')}
        \nЯ умею отслеживать твои результаты в пределах выбранной темы, чтобы после завершения теста ты мог прорешать заново те вопросы, на которых облажался.
        \nДля собственного удобства ты можешь периодически очищать чат со мной. Сам я этого делать не умею, увы... Средства, которыми я реализован, не позволяют мне очищать чат полностью.
        \nНапиши /help, чтобы узнать обо мне немного больше 🤫, или выбери эту команду в {html.code('Меню')}.\nДля того, чтобы выйти из выбранной темы, напиши /restart, или выбери эту команду в {html.code('Меню')}, но учти, что я забуду твой прогресс в покинутой теме!
        \nПогладь меня, пожалуйста, и я пущу тебя к вопросам...\n\n\n🥺👇
        """,
        reply_markup=keyboard
    )
    await asyncio.sleep(3)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


async def pet_me_button_handler(
        callback_query: CallbackQuery,
        session: Annotated[AsyncSession, Depends(get_async_session)]
):

    sections = await session.execute(select(Section))
    sections = sections.scalars().all()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{sections[0].title}", callback_data="section_1")],
        [InlineKeyboardButton(text=f"{sections[1].title}", callback_data="section_2")],
        [InlineKeyboardButton(text=f"{sections[2].title}", callback_data="section_3")]
    ])

    previous_message = callback_query.message
    await bot.delete_message(chat_id=previous_message.chat.id, message_id=previous_message.message_id)
    await callback_query.message.answer("Так уж и быть! Выбирай! 🐶❤️‍🔥", reply_markup=keyboard)


# noinspection PyTypeChecker
async def select_section_handler(
        callback_query: CallbackQuery,
        session: Annotated[AsyncSession, Depends(get_async_session)]
):

    chosen_section = int(callback_query.data[-1]) if callback_query.data.startswith("section") else int(callback_query.data[-1])
    themes = await session.execute(select(Theme).where(Theme.section_id == chosen_section))
    themes = themes.scalars().all()

    # Pagination logic
    start_page = 1 if callback_query.data.startswith("section") else int(callback_query.data[-3])
    per_page = 5  # Number of themes per page
    start_index = (start_page - 1) * per_page
    end_index = start_page * per_page

    # Create the inline keyboard markup
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    # Add theme buttons
    for i, theme in enumerate(themes[start_index:end_index]):
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=theme.title, callback_data=f"theme_{theme.id},{str(chosen_section)}")])

    # Add next page button if there are more themes
    last_page = False
    if len(themes) > end_index:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="➡️", callback_data=f"page_{start_page + 1},{str(chosen_section)}")])
    else:
        last_page = True

    # Add previous page button if not on the first page
    if start_page > 1:
        if last_page:
            keyboard.inline_keyboard.append([InlineKeyboardButton(text="⬅️", callback_data=f"page_{start_page - 1},{str(chosen_section)}")])
        else:
            keyboard.inline_keyboard[-1].insert(0, InlineKeyboardButton(text="⬅️", callback_data=f"page_{start_page - 1},{str(chosen_section)}"))

    keyboard.inline_keyboard.append([InlineKeyboardButton(text="◀️ К разделам", callback_data="pet")])

    previous_message = callback_query.message
    await bot.delete_message(chat_id=previous_message.chat.id, message_id=previous_message.message_id)
    await callback_query.message.answer(f"👩‍🎓 Раздел {'I' * chosen_section}:", reply_markup=keyboard)


# noinspection PyTypeChecker
async def select_theme_handler(
        callback_query: CallbackQuery,
        session: Annotated[AsyncSession, Depends(get_async_session)]
):

    temp_parser = callback_query.data.split(",")
    temp_parser[0] = temp_parser[0].split("_")[1]
    choosen_theme, choosen_section = temp_parser
    chosen_theme = await session.execute(select(Theme).where(Theme.id == int(choosen_theme)))
    chosen_theme = chosen_theme.scalars().first()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="◀️ К темам", callback_data="section_" + choosen_section),
            InlineKeyboardButton(text="Ехала ▶️", callback_data="quiz")
        ]
    ])

    previous_message = callback_query.message
    await bot.delete_message(chat_id=previous_message.chat.id, message_id=previous_message.message_id)
    await callback_query.message.answer(
        f"""
        ⚰️ Ставки сделаны, ставок больше нет... или есть?
        \nВы выбрали {html.italic(chosen_theme.title)}
        \nКнопки говорят сами за себя. Удачи.
        """, reply_markup=keyboard)


dp.callback_query.register(pet_me_button_handler, lambda c: c.data == 'pet')
dp.callback_query.register(select_section_handler, lambda c: c.data.startswith('section') or c.data.startswith('page'))
dp.callback_query.register(select_theme_handler, lambda c: c.data.startswith('theme'))


async def main() -> None:
    setup_di(dp)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
