"""Module for misc functions, used in middlewares."""

from aiogram.types import PollAnswer, CallbackQuery, Message

from services.utility_service import transliterate


def m_q_username(event: Message | CallbackQuery | PollAnswer) -> str:
    """
    Function, which collects username if incoming event is ``aiogram.Message`` or ``aiogram.CallbackQuery``.

    :param event: incoming event
    :return: collected username string
    """

    if event.from_user.username:
        username = event.from_user.username
    elif event.from_user.full_name:
        username = transliterate(event.from_user.full_name.replace(" ", "_")).lower()
    else:
        username = str(event.from_user.id)
    return username


def p_username(event: PollAnswer) -> str:
    """
    Function, which collects username if incoming event is ``aiogram.PollAnswer``.

    :param event: incoming event
    :return: collected username string
    """

    if event.user.username:
        username = event.user.username
    elif event.user.full_name:
        username = transliterate(event.user.full_name.replace(" ", "_")).lower()
    else:
        username = str(event.user.id)
    return username


def collect_username(event: Message | CallbackQuery | PollAnswer, flag: str) -> str:
    """
    Hub function for username collecting.

    :param event: incoming event
    :param flag: flag for event type

    :return: collected username string
    """

    match flag:
        case "m" | "q":
            return m_q_username(event)
        case "p":
            return p_username(event)
        case _:
            return "<unknown_username>"
