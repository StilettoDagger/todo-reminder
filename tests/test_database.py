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
    get_todo_by_message_id,
    update_todo_timestamp
)

@pytest.fixture
def db_connection():
    conn = sqlite3.connect(":memory:")
    initialize_db(conn)
    yield conn
    conn.close()

def test_channel_settings(db_connection):
    # Test setting and getting
    set_channel_settings(db_connection, channel_id=123, reminder_time=12, reminder_message="Hello {user}")
    settings = get_channel_settings(db_connection, channel_id=123)
    assert settings is not None
    assert settings["reminder_time"] == 12
    assert settings["reminder_message"] == "Hello {user}"

    # Test updating existing
    set_channel_settings(db_connection, channel_id=123, reminder_time=24, reminder_message="Update {user}")
    settings = get_channel_settings(db_connection, channel_id=123)
    assert settings["reminder_time"] == 24
    assert settings["reminder_message"] == "Update {user}"

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

def test_update_todo_timestamp(db_connection):
    now = datetime.datetime.now()
    past = now - datetime.timedelta(hours=25)
    
    # Create an overdue todo
    add_todo(db_connection, channel_id=1, message_id=33, user_id=111, created_at=past, updated_at=past, reminder_time=24)
    
    # Verify it is overdue
    overdue = get_overdue_todos(db_connection)
    assert any(t["message_id"] == 33 for t in overdue)
    
    # Update timestamp to now
    update_todo_timestamp(db_connection, message_id=33, updated_at=now)
    
    # Verify the database updated the field
    todo = get_todo_by_message_id(db_connection, 33)
    assert todo["updated_at"] == now.isoformat()
    
    # Verify it is no longer overdue
    overdue = get_overdue_todos(db_connection)
    assert not any(t["message_id"] == 33 for t in overdue)

def test_channel_settings_defaults(db_connection):
    # Set settings without reminder_time and reminder_message
    set_channel_settings(db_connection, channel_id=999)
    
    settings = get_channel_settings(db_connection, channel_id=999)
    assert settings["reminder_time"] == 24
    assert "{user}" in settings["reminder_message"]
    assert "{reminder_time}" in settings["reminder_message"]
    assert "{message_link}" in settings["reminder_message"]

def test_channel_settings_partial_update(db_connection):
    set_channel_settings(db_connection, channel_id=888, reminder_time=10, reminder_message="Initial msg")
    
    # Update only reminder_time
    set_channel_settings(db_connection, channel_id=888, reminder_time=20)
    settings = get_channel_settings(db_connection, channel_id=888)
    assert settings["reminder_time"] == 20
    assert settings["reminder_message"] == "Initial msg"
    
    # Update only reminder_message
    set_channel_settings(db_connection, channel_id=888, reminder_message="New msg")
    settings = get_channel_settings(db_connection, channel_id=888)
    assert settings["reminder_time"] == 20
    assert settings["reminder_message"] == "New msg"

def test_overdue_todos_invalid_date_format(db_connection):
    now = datetime.datetime.now()
    
    # Add a normal todo
    add_todo(db_connection, channel_id=1, message_id=44, user_id=111, created_at=now, updated_at=now, reminder_time=24)
    
    # Manually insert a todo with invalid date string into the database
    cursor = db_connection.cursor()
    cursor.execute(
        "INSERT INTO todos (channel_id, message_id, user_id, created_at, updated_at, reminder_time) VALUES (?, ?, ?, ?, ?, ?)",
        (1, 55, 111, "invalid_date", "invalid_date", 24)
    )
    db_connection.commit()
    
    # Calling get_overdue_todos shouldn't crash
    overdue = get_overdue_todos(db_connection)
    
    # We shouldn't get the invalid one, and since the normal one is recent, overdue should be empty
    assert len(overdue) == 0
