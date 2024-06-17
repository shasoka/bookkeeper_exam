from typing import Any

from sqlalchemy import ForeignKey, JSON, ARRAY, Integer
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import mapped_column, Mapped


class Base(AsyncAttrs, DeclarativeBase):
    type_annotation_map = {dict[str, Any]: JSON, list[int]: ARRAY(Integer)}


class Section(Base):
    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)

    themes: Mapped[list["Theme"]] = relationship("Theme", back_populates="section")


class Theme(Base):
    __tablename__ = "themes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)

    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"))

    section: Mapped["Section"] = relationship("Section", back_populates="themes")
    session: Mapped["UserSession"] = relationship("UserSession", back_populates="theme")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    answers: Mapped[dict[str, Any]] = mapped_column(nullable=False)
    correct_answer: Mapped[str] = mapped_column(nullable=False)

    theme_id: Mapped[int] = mapped_column(ForeignKey("themes.id"))


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[str] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column()
    checked_update: Mapped[bool] = mapped_column(nullable=False, default=False)
    help_alert_counter: Mapped[int] = mapped_column(nullable=False, default=0)
    themes_done_full: Mapped[list[int]] = mapped_column(nullable=False, default=[])
    themes_done_particular: Mapped[list[int]] = mapped_column(
        nullable=False, default=[]
    )

    session: Mapped["UserSession"] = relationship(
        "UserSession", back_populates="user", uselist=True
    )


class UserSession(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    theme_id: Mapped[int] = mapped_column(ForeignKey("themes.id"))
    incorrect_questions: Mapped[list[int]] = mapped_column(nullable=False)
    progress: Mapped[int] = mapped_column(nullable=False)
    questions_queue: Mapped[list[int]] = mapped_column(nullable=False)
    questions_total: Mapped[int] = mapped_column(nullable=False)
    hints: Mapped[int] = mapped_column()
    hints_total: Mapped[int] = mapped_column()
    cur_q_msg: Mapped[int] = mapped_column(nullable=True, default=None)
    cur_p_msg: Mapped[int] = mapped_column(nullable=True, default=None)
    cur_a_msg: Mapped[int] = mapped_column(nullable=True, default=None)
    cur_s_msg: Mapped[int] = mapped_column(nullable=False, default=None)

    user: Mapped["User"] = relationship("User", back_populates="session")
    theme: Mapped["Theme"] = relationship("Theme", back_populates="session")
