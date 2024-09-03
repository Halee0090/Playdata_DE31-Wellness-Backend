import pytest
from sqlalchemy.orm import Session
from app.database import get_db, engine

def test_get_db():
    db = next(get_db())
    assert isinstance(db, Session)
    db.close()

def test_database_connection():
    try:
        connection = engine.connect()
        assert connection is not None
    finally:
        connection.close()