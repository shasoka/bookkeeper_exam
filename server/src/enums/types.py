from typing import Coroutine, Any

from aiogram.types import Message, CallbackQuery, PollAnswer

# Event types for middlewares.miscellaneous.collect_username function
EVENT_TYPES = {
    Message: "m",
    CallbackQuery: "q",
    PollAnswer: "p",
}

# Return type for coroutines which return None
# 1. Any - type of values that the coro can yield
# 2. Any - type of values that the coro can accept
# 3. None - type of expecting return of the coro
CoroNoneReturn: Coroutine[Any, Any, None] = Coroutine[Any, Any, None]
