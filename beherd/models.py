from datetime import datetime
from typing import Optional

from flask_login import UserMixin
from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from beherd.extensions import db

MIN_CONTACTS = 1
MAX_CONTACTS = 5


class User(UserMixin, db.Model):
    """An account, identified by a verified phone number."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    preset: Mapped[Optional["Preset"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Preset(db.Model):
    """What gets sent, and to whom, when a user raises an alert."""

    __tablename__ = "presets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    # Stored normalized; see normalize_codeword().
    codeword: Mapped[str] = mapped_column(String(50))
    message: Mapped[str] = mapped_column(Text)

    user: Mapped[User] = relationship(back_populates="preset")
    contacts: Mapped[list["Contact"]] = relationship(
        back_populates="preset", cascade="all, delete-orphan", order_by="Contact.position"
    )

    @property
    def alert_body(self) -> str:
        return f"[BeHerd] {self.message} - {self.name}"


class Contact(db.Model):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    preset_id: Mapped[int] = mapped_column(ForeignKey("presets.id"))
    position: Mapped[int]
    name: Mapped[str | None] = mapped_column(String(100))
    # E.164, e.g. "+15705550100".
    phone: Mapped[str] = mapped_column(String(20))

    preset: Mapped[Preset] = relationship(back_populates="contacts")


def normalize_codeword(text: str) -> str:
    """Codewords match case-insensitively and ignore extra whitespace."""
    return " ".join(text.split()).lower()
