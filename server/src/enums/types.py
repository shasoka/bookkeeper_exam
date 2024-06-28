from typing import Coroutine, Any

from aiogram.types import Message, CallbackQuery, PollAnswer

from database.models import User

# Event types for middlewares.miscellaneous.collect_username function
EVENT_TYPES = {
    Message: "m",
    CallbackQuery: "q",
    PollAnswer: "p",
}

# --- # Types for coroutines # --- #

# 1. Any - type of values that the coro can yield
# 2. Any - type of values that the coro can accept
# 3. None - type of expecting return of the coro

# Return type for coroutines which return None
NoneFromCoroutine = Coroutine[Any, Any, None]

# Return type for coroutines which return User
UserFromCoroutine = Coroutine[Any, Any, User]
