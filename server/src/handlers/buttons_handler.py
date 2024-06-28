"""Module for inline buttons handlers."""


from aiogram import html
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from enums.markups import Markups, Buttons
from enums.strings import Messages, NavButtons, CallbackQueryAnswers, Markers
from handlers.utility_handlers import delete_msg_handler
from services.entities_service import (
    get_sections,
    get_themes_by_section,
    get_user,
    get_theme_by_id,
    get_questions_with_len_by_theme,
    update_themes_progress,
)


async def pet_me_button_pressed(callback_query: CallbackQuery | Message) -> None:
    """
    Function, that is called on ``aiogram.types.CallbackQuery`` with ``data`` property starting with ``pet``.

    :param callback_query: incoming ``aiogram.types.CallbackQuery`` object
    """

    sections = await get_sections()

    if isinstance(callback_query, CallbackQuery):
        await delete_msg_handler(callback_query)
        await callback_query.bot.send_message(
            chat_id=callback_query.message.chat.id,
            text=Messages.SECTIONS_FROM_START,
            reply_markup=Markups.sections_markup(sections),
            disable_notification=True,
        )
    else:
        await callback_query.bot.send_message(
            chat_id=callback_query.chat.id,
            text=Messages.SECTIONS_FROM_RESTART,
            reply_markup=Markups.sections_markup(sections),
            disable_notification=True,
        )


async def section_button_pressed(callback_query: CallbackQuery) -> None:
    """
    Function, that is called on ``aiogram.types.CallbackQuery`` with ``data`` property starting with ``section``.

    Creates markup for navigation between pages with themes in specific section.

    :param callback_query: incoming ``aiogram.types.CallbackQuery`` object
    """

    chosen_section = int(callback_query.data[-1])
    themes = await get_themes_by_section(chosen_section)
    user = await get_user(str(callback_query.from_user.id))
    start_page = (
        1 if callback_query.data.startswith("section") else int(callback_query.data[-3])
    )
    per_page = 5
    start_index = (start_page - 1) * per_page
    end_index = start_page * per_page
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    last_page = False

    # Adding themes to keyboard
    # 5 themes per page
    for i, theme in enumerate(themes[start_index:end_index]):
        if theme.id in user.themes_done_full:
            marker = Markers.GREEN
        elif theme.id in user.themes_done_particular:
            marker = Markers.YELLOW
        elif theme.id in user.themes_tried:
            marker = Markers.ORANGE
        else:
            marker = Markers.RED
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=marker + " " + theme.title,
                    callback_data=f"theme_{theme.id}_{str(chosen_section)}",
                )
            ]
        )

    # Next page button
    if len(themes) > end_index:
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=NavButtons.FORWARD_ARROW,
                    callback_data=f"page_{start_page + 1}_{str(chosen_section)}",
                )
            ]
        )
    else:
        last_page = True

    # Previous page button
    if start_page > 1:
        if last_page:
            keyboard.inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text=NavButtons.BACK_ARROW,
                        callback_data=f"page_{start_page - 1},{str(chosen_section)}",
                    )
                ]
            )
        else:
            keyboard.inline_keyboard[-1].insert(
                0,
                InlineKeyboardButton(
                    text=NavButtons.BACK_ARROW,
                    callback_data=f"page_{start_page - 1},{str(chosen_section)}",
                ),
            )

    # Back to sections button
    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(text=NavButtons.BACK_TO_SECTIONS, callback_data="pet")]
    )
    # Delete message button
    keyboard.inline_keyboard.append([Buttons.DELETE_BUTTON.value])

    await delete_msg_handler(callback_query)
    await callback_query.message.bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=Messages.ON_SECTIONS_CHOSEN % (Messages.ONE * chosen_section),
        reply_markup=keyboard,
        disable_notification=True,
    )


async def theme_button_pressed(callback_query: CallbackQuery) -> None:
    """
    Function, that is called on ``aiogram.types.CallbackQuery`` with ``data`` property starting with ``theme``.

    :param callback_query: incoming ``aiogram.types.CallbackQuery`` object
    """

    chosen_theme_from_callback, chosen_section = callback_query.data.split("_")[1:]
    chosen_theme = await get_theme_by_id(int(chosen_theme_from_callback))
    user = await get_user(str(callback_query.from_user.id))

    _, questions_total = await get_questions_with_len_by_theme(
        int(chosen_theme_from_callback)
    )

    await delete_msg_handler(callback_query)
    await callback_query.message.bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=Messages.ON_THEME_CHOSEN
        % (html.italic(chosen_theme.title), html.code(str(questions_total))),
        reply_markup=Markups.theme_chosen_markup(chosen_theme, user),
        disable_notification=True,
    )


async def mark_theme_as_done(callback_query: CallbackQuery) -> None:
    """
    Function, that is called on ``aiogram.types.CallbackQuery`` with ``data`` property starting with ``mark_theme``.

    :param callback_query: incoming ``aiogram.types.CallbackQuery`` object
    """

    theme, section = callback_query.data.split("_")[2:]

    await update_themes_progress(str(callback_query.from_user.id), int(theme), True)
    await callback_query.answer(CallbackQueryAnswers.THEME_MARKED)

    new_markup = callback_query.message.reply_markup
    new_markup.inline_keyboard[2] = [
        InlineKeyboardButton(
            text=NavButtons.BACK_TO_THEMES + " " + NavButtons.BACK_TRIANGLE,
            callback_data="section_" + section,
        )
    ]
    await callback_query.message.bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=new_markup,
    )
