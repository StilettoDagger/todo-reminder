import pytest
import sqlite3
import datetime
from src.database.connection import initialize_db
from src.database.queries import (
    set_channel_settings,
    get_channel_settings,
    add_todo,
    get_overdue_todos,
    delete_todo,
    get_todo_by_message_id
)

@pytest.fixture
def db_connection():
    conn = sqlite3.connect(":memory:")
    initialize_db(conn)
    yield conn
    conn.close()

def test_channel_settings(db_connection):
    # Test setting and getting
    set_channel_settings(db_connection, channel_id=123, reminder_time=12, reminder_message="Hello {user}", completion_reaction="👍")
    settings = get_channel_settings(db_connection, channel_id=123)
    assert settings is not None
    assert settings["reminder_time"] == 12
    assert settings["reminder_message"] == "Hello {user}"
    assert settings["completion_reaction"] == "👍"

    # Test updating existing
    set_channel_settings(db_connection, channel_id=123, reminder_time=24, reminder_message="Update {user}", completion_reaction="✅")
    settings = get_channel_settings(db_connection, channel_id=123)
    assert settings["reminder_time"] == 24
    assert settings["reminder_message"] == "Update {user}"
    assert settings["completion_reaction"] == "✅"

def test_todos(db_connection):
    now = datetime.datetime.now()
    
    # Add a todo
    add_todo(db_connection, channel_id=123, message_id=456, user_id=789, created_at=now, updated_at=now, reminder_time=24)
    
    # Get by message ID
    todo = get_todo_by_message_id(db_connection, 456)
    assert todo is not None
    assert todo["channel_id"] == 123
    assert todo["user_id"] == 789
    
    # Delete todo
    delete_todo(db_connection, 456)
    todo = get_todo_by_message_id(db_connection, 456)
    assert todo is None

def test_overdue_todos(db_connection):
    now = datetime.datetime.now()
    # 25 hours ago
    past = now - datetime.timedelta(hours=25)
    
    add_todo(db_connection, channel_id=1, message_id=11, user_id=111, created_at=past, updated_at=past, reminder_time=24)
    
    # Not overdue
    recent = now - datetime.timedelta(hours=2)
    add_todo(db_connection, channel_id=1, message_id=22, user_id=111, created_at=recent, updated_at=recent, reminder_time=24)
    
    overdue = get_overdue_todos(db_connection)
    assert len(overdue) == 1
    assert overdue[0]["message_id"] == 11
