from aiogram.types import InlineKeyboardButton

from database.models import UserSession
from resources.strings import HINT

DELETE_INLINE_BUTTON = InlineKeyboardButton(text="🗑", callback_data="delete")


# --- #


def get_hints_button(user_session: UserSession) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=HINT + f" ({user_session.hints}/{user_session.hints_total})", callback_data="hint")