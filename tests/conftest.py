from __future__ import annotations

import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["RABBITMQ_URL"] = ""
os.environ["MONGODB_URL"] = ""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure import db as db_module
from app.infrastructure.db import Base


@pytest.fixture(autouse=True)
def _fresh_sqlite_db() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    db_module._engine = engine
    db_module._Session = sessionmaker(engine, expire_on_commit=False)
    yield
    db_module._engine = None
    db_module._Session = None
