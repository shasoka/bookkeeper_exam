"""
Main module. Contains an entry point of the app.

Here the dispatcher and the bot are instantiated. Polling runs with :code:`concurrent.futures.ProcessPoolExecutor()`.
"""

import asyncio
import concurrent.futures

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config import TG_TOKEN as TOKEN, BASE_WEBHOOK_URL, WEBHOOK_PATH, WEBHOOK_SECRET, WEB_SERVER_PORT, WEB_SERVER_HOST
from handlers.buttons_handler import pet_me_button_pressed, theme_button_pressed, section_button_pressed, \
    mark_theme_as_done
from handlers.commands_handler import command_start_handler, command_restart_handler, command_exam_handler, \
    command_heal_handler, command_change_hints_policy_handler
from handlers.exam_handler import exam
from handlers.utility_handlers import delete_msg_handler
from handlers.poll_handler import on_poll_answer
from handlers.quiz_handler import quiz, hint_requested
from middlewares.auth_mw import AuthMiddleware
from middlewares.log_mw import LoggingMiddleware
from middlewares.update_mw import LastChangelogMiddleware
from resources.strings import CHANGE_HINTS_POLICY_COMMAND, RESTART_COMMAND, HEAL_COMMAND, EXAM_COMMAND


dp: Dispatcher = Dispatcher()
"""*Module-scoped*. Aiogram Dispatcher object (root router)"""

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

for handler in [dp.message, dp.callback_query, dp.poll_answer]:
    handler.outer_middleware(LoggingMiddleware())

dp.message.outer_middleware(AuthMiddleware())
dp.message.outer_middleware(LastChangelogMiddleware())

dp.message.register(command_start_handler, CommandStart())
dp.message.register(command_restart_handler, Command(RESTART_COMMAND))
dp.message.register(command_exam_handler, Command(EXAM_COMMAND))
dp.message.register(command_heal_handler, Command(HEAL_COMMAND))
dp.message.register(command_change_hints_policy_handler, Command(CHANGE_HINTS_POLICY_COMMAND))

dp.callback_query.register(pet_me_button_pressed, lambda c: c.data == "pet")
dp.callback_query.register(theme_button_pressed, lambda c: c.data.startswith("theme"))
dp.callback_query.register(quiz, lambda c: c.data.startswith("quiz"))
dp.callback_query.register(exam, lambda c: c.data.startswith("exam"))
dp.callback_query.register(delete_msg_handler, lambda c: c.data == "delete")
dp.callback_query.register(section_button_pressed, lambda c: c.data.startswith("section") or c.data.startswith("page"))
dp.callback_query.register(hint_requested, lambda c: c.data.startswith("hint"))
dp.callback_query.register(mark_theme_as_done, lambda c: c.data.startswith("mark_theme_"))

dp.poll_answer.register(on_poll_answer)


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(
        url=f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}",
        secret_token=WEBHOOK_SECRET
    )


async def main() -> None:
    # dp.startup.register(on_startup)
    #
    # app = web.Application()
    #
    # webhook_requests_handler = SimpleRequestHandler(
    #     dispatcher=dp,
    #     bot=bot,
    #     secret_token=WEBHOOK_SECRET,
    # )
    # # Register webhook handler on application
    # webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    #
    # # Mount dispatcher startup and shutdown hooks to aiohttp application
    # setup_application(app, dp, bot=bot)

    # Run in a custom process pool to prevent IO blocking
    with concurrent.futures.ProcessPoolExecutor() as _:
        await dp.start_polling(bot)  # For long-polling mode
        # web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    asyncio.run(main())  # For long-polling mode
    # main()
