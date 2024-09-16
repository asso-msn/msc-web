import datetime
from pathlib import Path

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped as Column
from sqlalchemy.orm import mapped_column as column
from sqlalchemy.orm import relationship

from app import config

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
    illustration: Column[str] = column(nullable=True)

    author = relationship("User", back_populates="submissions")
    event = relationship("Event", back_populates="submissions")
    files = relationship("File", back_populates="submission")

    @property
    def path(self):
        return Path(config.UPLOAD_DIR) / self.event_id / str(self.id)

    @property
    def illustration_path(self):
        if not self.illustration:
            return None
        return self.path / self.illustration

    @staticmethod
    def get_default_name(title, artist):
        return f"{artist} - {title}"

    @property
    def artist(self):
        if " - " not in self.name:
            return None
        return self.name.split(" - ", 1)[0]

    @property
    def title(self):
        if " - " not in self.name:
            return None
        return self.name.split(" - ", 1)[1]
