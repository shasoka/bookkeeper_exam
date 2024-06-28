"""Module, that stores string constants for logging."""


from enum import StrEnum
from typing import Final


class Logs(StrEnum):
    """Enum class with strings for logging."""

    # Emoji-tags
    LOCK: Final[str] = "🔒"
    UNLOCK: Final[str] = "🔓"
    MESSAGE: Final[str] = "💬"
    CALLBACK: Final[str] = "📞"
    ANSWER: Final[str] = "🔑"
    COMMAND: Final[str] = "🤖"

    # Log messages
    COULDN_DELETE_MSG: Final[str] = "[❌🧹] Couldn't delete msg=%s in chat with user=%s"

    AVG_TIMING: Final[str] = "[⏳] Average timing for 25 last requsts: %.5f"

    CHANGE_LOG_SEEN: Final[str] = "[🗄] Changelog seen by %s"

    EXAM_RECORD: Final[str] = "[✴️] New exam record updated by %s"

    EXAM_TIMEOUT: Final[str] = "[⏰] Exam timed out for %s"

    COULDNT_SEND_MSG_WITH_EFFECT: Final[str] = "[❌💬] Couldn't send msg with effect=%s"

    TOO_MANY_SESSIONS: Final[str] = "[♻️] Too many sessions for %s"

    CORRECT_ANS: Final[str] = "[✅] Correct answer from %s"

    INCORRECT_ANS: Final[str] = "[❌] Incorrect answer from %s"

    SESSION_BROKEN: Final[str] = "[🫠] Session=%s was broken by %s"

    # Running modes
    WEBHOOK_MODE: Final[str] = "[🌐] Running in --webhook mode"
    POLLING_MODE: Final[str] = "[🔨] Running in --polling mode"
