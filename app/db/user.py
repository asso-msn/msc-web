from sqlalchemy.orm import Mapped as Column
from sqlalchemy.orm import mapped_column as column
from sqlalchemy.orm import relationship

from . import Base


class User(Base):
    id: Column[int] = column(primary_key=True)
    username: Column[str]

    submissions = relationship("Submission", back_populates="author")
