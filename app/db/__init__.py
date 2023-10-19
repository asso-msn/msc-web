from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, declared_attr

from app import config


class Base(DeclarativeBase):
    prefix = False

    @declared_attr.directive
    def __tablename__(cls) -> str:
        name = ""
        for c in cls.__name__:
            if name and name[-1] != "_" and c.isupper():
                name += "_"
            name += c.lower()

        if not name.endswith("s"):
            name += "s"
        if cls.prefix:
            if isinstance(cls.prefix, str):
                prefix = cls.prefix
            name = f"{prefix}_{name}"
        return name


class Database:
    """
    Helper class to manage the database connection and session
    Exposes the SQLAlchemy Base and Session objects
    """

    def __init__(self, uri: str = config.DATABASE_URI):
        protocol, path = uri.split("://", 1)
        # We override some protocols as the URI should not show any Python
        # specific stuff
        if protocol == "sqlite":
            target = Path(path.split("/", 1)[1])
            target.parent.mkdir(parents=True, exist_ok=True)
        protocol = {
            "sqlite": "sqlite+pysqlite",
        }.get(protocol, protocol)
        uri = f"{protocol}://{path}"
        self.engine = create_engine(uri)

    @contextmanager
    def session(self) -> Iterator[Session]:
        with Session(self.engine, expire_on_commit=False) as s:
            # Disabling expire_on_commit allows us to access the objects after
            # the session is closed or committed, which happens as soon as the
            # context manager exits
            with s.begin():
                yield s

    def init(self):
        """
        Create the tables in the database
        """
        Base.metadata.create_all(self.engine)


connection = Database()
session = connection.session


def get(table, *id):
    with connection.session() as s:
        try:
            obj = s.get(table, id)
        except sa.exc.NoResultFound:
            raise Exception(f"No {table} {id}")  # TODO: make this a 404
    return obj


from .event import Event
from .file import File
from .submission import Submission
from .user import User
