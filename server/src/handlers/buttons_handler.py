from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from handlers.utility_handlers import delete_msg_handler
from resources.reply_markups import DELETE_INLINE_BUTTON
from resources.strings import SECTIONS_FROM_START, SECTIONS_FROM_RESTART, FORWARD, BACK, \
    BACK_TO_SECTIONS, on_section_chosen, LETS_GO, LETS_SHUFFLE, BACK_TO_THEMES, MARK_THEME, on_theme_chosen
from services.entities_service import get_sections, get_themes_by_section, get_user, get_theme_by_id, \
    get_questions_with_len_by_theme, update_themes_progress


# noinspection PyTypeChecker
async def pet_me_button_pressed(callback_query: CallbackQuery | Message) -> None:
    sections = await get_sections()
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
        await delete_msg_handler(callback_query)
        await callback_query.bot.send_message(
            chat_id=callback_query.message.chat.id,
            text=SECTIONS_FROM_START,
            reply_markup=keyboard,
            disable_notification=True,
        )
    else:
        await callback_query.bot.send_message(
            chat_id=callback_query.chat.id,
            text=SECTIONS_FROM_RESTART,
            reply_markup=keyboard,
            disable_notification=True,
        )


# noinspection PyTypeChecker
async def section_button_pressed(callback_query: CallbackQuery) -> None:
    chosen_section = int(callback_query.data[-1])
    themes = await get_themes_by_section(chosen_section)
    user = await get_user(str(callback_query.from_user.id))
    start_page = (1 if callback_query.data.startswith("section") else int(callback_query.data[-3]))
    per_page = 5
    start_index = (start_page - 1) * per_page
    end_index = start_page * per_page
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    last_page = False

    # Добавление кнопок тем
    for i, theme in enumerate(themes[start_index:end_index]):
        if theme.id in user.themes_done_full:
            marker = "🟢"
        elif theme.id in user.themes_done_particular:
            marker = "🟡"
        elif theme.id in user.themes_tried:
            marker = "🟠"
        else:
            marker = "🔴"
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=marker + " " + theme.title,
                    callback_data=f"theme_{theme.id}_{str(chosen_section)}",
                )
            ]
        )

    # Добавление кнопки перехода на следующую страницу
    if len(themes) > end_index:
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=FORWARD,
                    callback_data=f"page_{start_page + 1}_{str(chosen_section)}",
                )
            ]
        )
    else:
        last_page = True

    # Добавление кнопки перехода на предыдущую страницу
    if start_page > 1:
        if last_page:
            keyboard.inline_keyboard.append(
                [
                    InlineKeyboardButton(
                        text=BACK,
                        callback_data=f"page_{start_page - 1},{str(chosen_section)}",
                    )
                ]
            )
        else:
            keyboard.inline_keyboard[-1].insert(
                0,
                InlineKeyboardButton(
                    text=BACK,
                    callback_data=f"page_{start_page - 1},{str(chosen_section)}",
                ),
            )

    # Добавление кнопки возвращения к разделам
    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(text=BACK_TO_SECTIONS, callback_data="pet")]
    )
    # Добавление кнопки удаления сообщения
    keyboard.inline_keyboard.append([DELETE_INLINE_BUTTON])

    await delete_msg_handler(callback_query)
    await callback_query.message.bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=on_section_chosen(chosen_section),
        reply_markup=keyboard,
        disable_notification=True,
    )


# noinspection PyTypeChecker
async def theme_button_pressed(callback_query: CallbackQuery) -> None:
    chosen_theme_from_callback, choosen_section = callback_query.data.split("_")[1:]
    chosen_theme = await get_theme_by_id(int(chosen_theme_from_callback))
    user = await get_user(str(callback_query.from_user.id))

    _, questions_total = await get_questions_with_len_by_theme(int(chosen_theme_from_callback))

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=LETS_GO,
                    callback_data="quiz_init_" + chosen_theme_from_callback,
                )
            ],
            [
                InlineKeyboardButton(
                    text=LETS_SHUFFLE,
                    callback_data="quiz_init_shuffle_" + chosen_theme_from_callback,
                )
            ],
            (
                [
                    InlineKeyboardButton(
                        text=BACK_TO_THEMES, callback_data="section_" + choosen_section
                    ),
                    InlineKeyboardButton(
                        text=MARK_THEME,
                        callback_data="mark_theme_"
                        + str(chosen_theme.id)
                        + "_"
                        + str(choosen_section),
                    ),
                ]
                if chosen_theme.id not in user.themes_done_full
                else [
                    InlineKeyboardButton(
                        text=BACK_TO_THEMES + " ◀️",
                        callback_data="section_" + choosen_section,
                    )
                ]
            ),
            [DELETE_INLINE_BUTTON],
        ]
    )

    await delete_msg_handler(callback_query)
    await callback_query.message.bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=on_theme_chosen(chosen_theme.title, str(questions_total)),
        reply_markup=keyboard,
        disable_notification=True,
    )


async def mark_theme_as_done(callback_query: CallbackQuery) -> None:
    theme, section = callback_query.data.split("_")[2:]

    await update_themes_progress(str(callback_query.from_user.id), int(theme), True)
    await callback_query.answer("✅")

    new_markup = callback_query.message.reply_markup
    new_markup.inline_keyboard[2] = [
        InlineKeyboardButton(
            text=BACK_TO_THEMES + " ◀️", callback_data="section_" + section
        )
    ]
    await callback_query.message.bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=new_markup
    )
