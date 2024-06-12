from typing import Any

from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import mapped_column, Mapped


class Base(DeclarativeBase):
    type_annotation_map = {
        dict[str, Any]: JSON
    }


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


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    answers: Mapped[dict[str, Any]] = mapped_column(nullable=False)
    correct_answer: Mapped[str] = mapped_column(nullable=False)

    theme_id: Mapped[int] = mapped_column(ForeignKey("themes.id"))
