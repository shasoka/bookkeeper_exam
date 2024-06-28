"""
Module, that stores constants of ``aiogram.types.InlineKeyboardButton``, ``aiogram.types.InlineKeyboardMarkup`` types
and some constructor functions, which return more complicated markups.
"""


from enum import Enum
from typing import Final

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.models import UserSession, Section, Theme, User
from enums.strings import MiscButtons, NavButtons


class Buttons(Enum):
    """Enum class with ``aiogram.types.InlineKeyboardButton`` constants."""

    DELETE_BUTTON: Final[InlineKeyboardButton] = InlineKeyboardButton(
        text=MiscButtons.DELETE, callback_data="delete"
    )

    SOLVE_INCORRECTS: Final[InlineKeyboardButton] = InlineKeyboardButton(
        text=MiscButtons.PUZZLE, callback_data="quiz_incorrect"
    )

    PET_BUTTON: Final[InlineKeyboardButton] = InlineKeyboardButton(
        text=MiscButtons.PET_ME, callback_data="pet"
    )

    FIGHT_BUTTON: Final[InlineKeyboardButton] = InlineKeyboardButton(
        text=MiscButtons.FIGHT_ME, callback_data="exam_init"
    )


class Markups(Enum):
    """
    Enum class with ``aiogram.types.InlineKeyboardMarkup`` constants
    and methods with same return-type.
    """

    # Markup for quiz summary message
    QUIZ_S_MSG_MARKUP: Final[InlineKeyboardMarkup] = InlineKeyboardMarkup(
        inline_keyboard=[
            [Buttons.SOLVE_INCORRECTS.value],
            [Buttons.DELETE_BUTTON.value],
        ]
    )

    # Markup for messages with only delete button
    ONLY_DELETE_MARKUP: Final[InlineKeyboardMarkup] = InlineKeyboardMarkup(
        inline_keyboard=[[Buttons.DELETE_BUTTON.value]]
    )

    # Markup for on-start-message
    PET_ME_MARKUP: Final[InlineKeyboardMarkup] = InlineKeyboardMarkup(
        inline_keyboard=[[Buttons.PET_BUTTON.value], [Buttons.DELETE_BUTTON.value]]
    )

    # Markup for pre-exam message
    FIGHT_ME_MARKUP: Final[InlineKeyboardMarkup] = InlineKeyboardMarkup(
        inline_keyboard=[[Buttons.FIGHT_BUTTON.value], [Buttons.DELETE_BUTTON.value]]
    )

    @staticmethod
    def only_hints_markup(user_session: UserSession) -> InlineKeyboardMarkup:
        """
        Method, that returns markup for quiz question-message.

        Markup will be applied to message only if ``hints_allowed==True``.

        :param user_session: current user session
        :return: gathered markup
        """

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=MiscButtons.HINT
                        + f" ({user_session.hints}/{user_session.hints_total})",
                        callback_data="hint",
                    )
                ]
            ]
        )

    @staticmethod
    def sections_markup(sections: list[Section]) -> InlineKeyboardMarkup:
        """
        Method, that returns markup for section-selection message.

        :param sections: list of available sections
        :return: gathered markup
        """

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"{sections[0].title}", callback_data="section_1"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=f"{sections[1].title}", callback_data="section_2"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=f"{sections[2].title}", callback_data="section_3"
                    )
                ],
                [Buttons.DELETE_BUTTON.value],
            ]
        )

    @staticmethod
    def theme_chosen_markup(theme: Theme, user: User) -> InlineKeyboardMarkup:
        """
        Method, that returns markup for pre-quiz message.

        :param theme: chosen theme
        :param user: current user
        :return: gathered markup
        """

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=NavButtons.LETS_GO,
                        callback_data="quiz_init_" + str(theme.id),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=NavButtons.LETS_SHUFFLE,
                        callback_data="quiz_init_shuffle_" + str(theme.id),
                    )
                ],
                (
                    [
                        InlineKeyboardButton(
                            text=NavButtons.BACK_TO_THEMES,
                            callback_data="section_" + str(theme.id),
                        ),
                        InlineKeyboardButton(
                            text=MiscButtons.MARK_THEME,
                            callback_data="mark_theme_"
                            + str(theme.id)
                            + "_"
                            + str(theme.section_id),
                        ),
                    ]
                    if theme.id not in user.themes_done_full
                    else [
                        InlineKeyboardButton(
                            text=NavButtons.BACK_TO_THEMES + " ◀️",
                            callback_data="section_" + str(theme.section_id),
                        )
                    ]
                ),
                [Buttons.DELETE_BUTTON.value],
            ]
        )

    @staticmethod
    def next_question_markup(next_q: bool, callback_data: str) -> InlineKeyboardMarkup:
        """
        Method, that returns markup for quiz answer-message.

        :param next_q: flag, whether the next question is available or last question was answered
        :param callback_data: data of incoming ``aiogram.types.CallbackQuery`` object
        :return: gathered markup
        """

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=(
                            NavButtons.FORWARD_ARROW if next_q else NavButtons.FINISH
                        ),
                        callback_data=callback_data,
                    )
                ]
            ]
        )
