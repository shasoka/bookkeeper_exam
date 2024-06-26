from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command

from config import TG_TOKEN as TOKEN
from enums.strings import SlashCommands
from handlers.buttons_handler import pet_me_button_pressed, theme_button_pressed, section_button_pressed, \
    mark_theme_as_done
from handlers.commands_handler import command_start_handler, command_change_hints_policy_handler, command_heal_handler, \
    command_exam_handler, command_restart_handler
from handlers.exam_handler import exam
from handlers.poll_handler import on_poll_answer
from handlers.quiz_handler import quiz, hint_requested
from handlers.utility_handlers import delete_msg_handler
from middlewares.auth_middleware import AuthMiddleware
from middlewares.log_middleware import LoggingMiddleware
from middlewares.update_middleware import LastChangelogMiddleware


def setup() -> tuple[Dispatcher, Bot]:
    dp: Dispatcher = Dispatcher()
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    register_handlers(dp)

    return dp, bot


def register_handlers(dp: Dispatcher) -> None:

    for handler in [dp.message, dp.callback_query, dp.poll_answer]:
        handler.outer_middleware(LoggingMiddleware())

    dp.message.outer_middleware(AuthMiddleware())
    dp.message.outer_middleware(LastChangelogMiddleware())

    dp.message.register(command_start_handler, CommandStart())
    dp.message.register(command_restart_handler, Command(SlashCommands.RESTART))
    dp.message.register(command_exam_handler, Command(SlashCommands.EXAM))
    dp.message.register(command_heal_handler, Command(SlashCommands.HEAL))
    dp.message.register(command_change_hints_policy_handler, Command(SlashCommands.HINTS_POLICY))

    dp.callback_query.register(pet_me_button_pressed, lambda c: c.data == "pet")
    dp.callback_query.register(theme_button_pressed, lambda c: c.data.startswith("theme"))
    dp.callback_query.register(quiz, lambda c: c.data.startswith("quiz"))
    dp.callback_query.register(exam, lambda c: c.data.startswith("exam"))
    dp.callback_query.register(delete_msg_handler, lambda c: c.data == "delete")
    dp.callback_query.register(section_button_pressed, lambda c: c.data.startswith("section") or c.data.startswith("page"))
    dp.callback_query.register(hint_requested, lambda c: c.data.startswith("hint"))
    dp.callback_query.register(mark_theme_as_done, lambda c: c.data.startswith("mark_theme_"))

    dp.poll_answer.register(on_poll_answer)
