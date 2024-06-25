from typing import Coroutine, Any

CoroNoneReturn: Coroutine[Any, Any, None] = Coroutine[Any, Any, None]
# 1. Any - type of values that the coro can yield
# 2. Any - type of values that the coro can accept
# 3. None - type of expecting return of the coro
