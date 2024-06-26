from aiogram.types import PollAnswer, CallbackQuery, Message

from services.utility_service import transliterate


def m_q_username(event: Message | CallbackQuery | PollAnswer) -> str:
    if event.from_user.username:
        username = event.from_user.username
    elif event.from_user.full_name:
        username = transliterate(event.from_user.full_name.replace(" ", "_")).lower()
    else:
        username = str(event.from_user.id)
    return username


def p_username(event: PollAnswer) -> str:
    if event.user.username:
        username = event.user.username
    elif event.user.full_name:
        username = transliterate(event.user.full_name.replace(" ", "_")).lower()
    else:
        username = str(event.user.id)
    return username


def collect_username(event: Message | CallbackQuery | PollAnswer, flag: str) -> str:
    match flag:
        case "m" | "q":
            return m_q_username(event)
        case "p":
            return p_username(event)
        case _:
            return "<unknown_username>"
