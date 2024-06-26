import asyncio
from concurrent import futures

import click
from aiogram import Bot
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config import BASE_WEBHOOK_URL, WEBHOOK_PATH, WEBHOOK_SECRET, WEB_SERVER_HOST, WEB_SERVER_PORT
from setup import setup


@click.command
@click.option('--webhook', is_flag=True, help="Run the bot in webhook mode")
@click.option('--polling', is_flag=True, help="Run the bot in polling mode")
def main(webhook: bool, polling: bool) -> None:
    if webhook:
        _webhook_mode()
    elif polling:
        asyncio.run(_polling_mode())
    else:
        click.echo("Please specify a mode: --webhook or --polling")


async def __set_wh(bot: Bot) -> None:
    await bot.set_webhook(
        url=f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}",
        secret_token=WEBHOOK_SECRET
    )


def _webhook_mode() -> None:
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
    # Get dispatcher and bot
    dp, bot = setup()

    # Run in a custom process pool to prevent IO blocking
    with futures.ProcessPoolExecutor():
        await dp.start_polling(bot)  # For long-polling mode
