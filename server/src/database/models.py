"""Module for ORM models."""


from sqlalchemy import ForeignKey, ARRAY, Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import mapped_column, Mapped


class Base(AsyncAttrs, DeclarativeBase):
    """SQLAlchemy base class."""

    # Annotations
    type_annotation_map = {
        list[str]: ARRAY(String),
        list[int]: ARRAY(Integer)
    }


class Section(Base):
    """ORM model for ``sections`` table."""

    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)

    themes: Mapped[list["Theme"]] = relationship("Theme", back_populates="section")


class Theme(Base):
    """ORM model for ``themes`` table."""

    __tablename__ = "themes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)

    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"))

    section: Mapped["Section"] = relationship("Section", back_populates="themes")
    session: Mapped["UserSession"] = relationship("UserSession", back_populates="theme")
    questions: Mapped[list["Question"]] = relationship(
        "Question", back_populates="theme"
    )


class Question(Base):
    """ORM model for ``questions`` table."""

    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    answers: Mapped[list[str]] = mapped_column(nullable=False)
    correct_answer: Mapped[str] = mapped_column(nullable=False)

    theme_id: Mapped[int] = mapped_column(ForeignKey("themes.id"))

    theme: Mapped["Theme"] = relationship("Theme", back_populates="questions")


class User(Base):
    """ORM model for ``users`` table."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[str] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column()
    exam_best: Mapped[int] = mapped_column(nullable=False, default=0)
    hints_allowed: Mapped[bool] = mapped_column(nullable=False, default=True)
    checked_update: Mapped[bool] = mapped_column(nullable=False, default=False)
    help_alert_counter: Mapped[int] = mapped_column(nullable=False, default=0)
    themes_tried: Mapped[list[int]] = mapped_column(nullable=False, default=[])
    themes_done_full: Mapped[list[int]] = mapped_column(nullable=False, default=[])
    themes_done_particular: Mapped[list[int]] = mapped_column(
        nullable=False, default=[]
    )

    session: Mapped["UserSession"] = relationship(
        "UserSession", back_populates="user", uselist=True
    )


class UserSession(Base):
    """ORM model for ``sessions`` table."""
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
