import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped as Column
from sqlalchemy.orm import mapped_column as column
from sqlalchemy.orm import relationship

from . import Base


class Submission(Base):
    id: Column[int] = column(primary_key=True)
    event_id: Column[str] = column(ForeignKey("events.id"), primary_key=True)
    created_at: Column[datetime.datetime] = column(
        default=datetime.datetime.utcnow
    )
    updated_at: Column[datetime.datetime] = column(
        default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
    author_id: Column[int] = column(ForeignKey("users.id"))
    name: Column[str]
    draft: Column[bool] = column(default=True)

    author = relationship("User", back_populates="submissions")
    event = relationship("Event", back_populates="submissions")
    files = relationship("File", back_populates="submission")
