import datetime
import enum

from sqlalchemy.orm import Mapped as Column
from sqlalchemy.orm import mapped_column as column
from sqlalchemy.orm import relationship

from . import Base


class SubmissionType(enum.Enum):
    sdvx = enum.auto()


ARCHIVE_EXTENSIONS = ["zip", "7z", "rar", "tar", "tar.gz"]


class Event(Base):
    id: Column[str] = column(primary_key=True)
    name: Column[str]
    description: Column[str]
    start_date: Column[datetime.date] = column(nullable=True)
    end_date: Column[datetime.date] = column(nullable=True)
    type: Column[SubmissionType] = column(nullable=True)

    submissions: Column[list["Submission"]] = relationship(
        back_populates="event"
    )

    @property
    def allowed_extensions(self):
        return ARCHIVE_EXTENSIONS
