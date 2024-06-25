from enum import StrEnum
from typing import Final


class Logs(StrEnum):

    LOCK: Final[str] = "🔒"
    UNLOCK: Final[str] = "🔓"

    COULDN_DELETE_MSG: Final[str] = "[❌🧹] Couldn't delete msg=%s in chat with user=%s"

    AVG_TIMING: Final[str] = "[⏳] Average timing for 25 last requsts: %.5f"
