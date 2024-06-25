"""
Main module. Contains an entry point of the app.

Here the dispatcher and the bot are instantiated. Polling runs with :code:`concurrent.futures.ProcessPoolExecutor()`.
"""

import asyncio
import concurrent.futures

from setup import setup, webhook


async def main() -> None:
    dp, bot = setup()

    # dp.startup.register(webhook)
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
