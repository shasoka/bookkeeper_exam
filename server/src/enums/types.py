"""Module, that stores types alias."""


from aiogram.types import Message, CallbackQuery, PollAnswer

# About coroutine return values
#                                         [1]  [2]   [3]
#                                          ↓    ↓     ↓
# Basically async def func() -> Coroutine[Any, Any, None], where:
# 1. Type of values that the coro can yield
# 2. Type of values that the coro can accept
# 3. Type of expecting return of the coro

# Event types for middlewares.miscellaneous.collect_username function
EVENT_TYPES = {
    Message: "m",
    CallbackQuery: "q",
    PollAnswer: "p",
}
