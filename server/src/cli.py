"""
Module, which contains the command line interface (CLI) for the bot.

There are only two options:
    - ``--webhook`` for running in webhook mode
    - ``--polling`` for running in polling mode
"""


import asyncio
from concurrent import futures

import click
from aiogram import Bot
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config import BASE_WEBHOOK_URL, WEBHOOK_PATH, WEBHOOK_SECRET, WEB_SERVER_HOST, WEB_SERVER_PORT
from enums.logs import Logs
from loggers.setup import LOGGER
from setup import setup


@click.command
@click.option('--webhook', is_flag=True, help="Run the bot in webhook mode")
@click.option('--polling', is_flag=True, help="Run the bot in polling mode")
def main(webhook: bool, polling: bool) -> None:
    """
    Click-decorated function for CLI.

    :param webhook: boolean flag for webhook mode, defaults to ``False`` if not specified
    :param polling: boolean flag for polling mode, defaults to ``False`` if not specified
    """

    if webhook:
        LOGGER.info(Logs.WEBHOOK_MODE)
        _webhook_mode()
    elif polling:
        LOGGER.info(Logs.POLLING_MODE)
        asyncio.run(_polling_mode())
    else:
        click.echo("Please specify a mode: --webhook or --polling")


async def __set_wh(bot: Bot) -> None:
    """
    Function, which sets webhook for the bot.

    Runs on dispatcher startup.

    :param bot: instance of ``aiogram.Bot``
    """

    await bot.set_webhook(
        url=f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}",
        secret_token=WEBHOOK_SECRET
    )


def _webhook_mode() -> None:
    """
    Function, that runs the bot in webhook mode.

    ``http.web.run_app`` runs in separated process.
    """

    # Get dispatcher and bot
    dp, bot = setup()

    # Set webhook for the bot
    dp.startup.register(__set_wh)

    # Create aiohttp application
    app = web.Application()

    # Create webhook requests handler
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )

    # Register webhook handler on application
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)

    # Run in a custom process pool to prevent IO blocking
    with futures.ProcessPoolExecutor():
        web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


async def _polling_mode() -> None:
    """
    Function, that runs the bot in long polling mode.

    ``aiogram.Dispatcher.start_polling`` runs in separated process.
    """

    # Get dispatcher and bot
    dp, bot = setup()

    # Run in a custom process pool to prevent IO blocking
    with futures.ProcessPoolExecutor():
        await dp.start_polling(bot)  # For long-polling mode
