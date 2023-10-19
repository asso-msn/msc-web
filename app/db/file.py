from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped as Column
from sqlalchemy.orm import mapped_column as column
from sqlalchemy.orm import relationship

from . import Base


class File(Base):
    id: Column[int] = column(primary_key=True)
    path: Column[str]
    hash: Column[str]
    submission_id: Column[int] = column(ForeignKey("submissions.id"))

    submission = relationship("Submission", back_populates="files")
