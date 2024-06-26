"""
Main module. Contains an entry point of the app.

Here the dispatcher and the bot are instantiated. Polling runs with :code:`concurrent.futures.ProcessPoolExecutor()`.
"""

from cli import main


if __name__ == "__main__":
    main()
