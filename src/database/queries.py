import datetime

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def set_channel_settings(conn, channel_id, reminder_time=None, reminder_message=None):
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    # Check if exists
    cursor.execute("SELECT * FROM channel_settings WHERE channel_id = ?", (channel_id,))
    existing = cursor.fetchone()
    
    if existing:
        query = "UPDATE channel_settings SET "
        params = []
        updates = []
        
        if reminder_time is not None:
            updates.append("reminder_time = ?")
            params.append(reminder_time)
        if reminder_message is not None:
            updates.append("reminder_message = ?")
            params.append(reminder_message)
            
        if updates:
            query += ", ".join(updates) + " WHERE channel_id = ?"
            params.append(channel_id)
            cursor.execute(query, params)
    else:
        # Defaults
        rt = reminder_time if reminder_time is not None else 24
        rm = reminder_message if reminder_message is not None else "{user} hasn't updated their todo in {reminder_time} hours: {message_link}"
        
        cursor.execute(
            "INSERT INTO channel_settings (channel_id, reminder_time, reminder_message) VALUES (?, ?, ?)",
            (channel_id, rt, rm)
        )
    
    conn.commit()

def get_channel_settings(conn, channel_id):
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM channel_settings WHERE channel_id = ?", (channel_id,))
    return cursor.fetchone()

def add_todo(conn, channel_id, message_id, user_id, created_at, updated_at, reminder_time):
    cursor = conn.cursor()
    created_at_str = created_at.isoformat() if isinstance(created_at, datetime.datetime) else created_at
    updated_at_str = updated_at.isoformat() if isinstance(updated_at, datetime.datetime) else updated_at
    cursor.execute(
        "INSERT INTO todos (channel_id, message_id, user_id, created_at, updated_at, reminder_time) VALUES (?, ?, ?, ?, ?, ?)",
        (channel_id, message_id, user_id, created_at_str, updated_at_str, reminder_time)
    )
    conn.commit()

def get_todo_by_message_id(conn, message_id):
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM todos WHERE message_id = ?", (message_id,))
    return cursor.fetchone()

def delete_todo(conn, message_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todos WHERE message_id = ?", (message_id,))
    conn.commit()

def get_overdue_todos(conn):
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    now = datetime.datetime.now()
    
    cursor.execute("SELECT * FROM todos")
    todos = cursor.fetchall()
    
    overdue = []
    for todo in todos:
        # Convert updated_at string back to datetime if it's a string
        updated_at = todo["updated_at"]
        if isinstance(updated_at, str):
            try:
                updated_at = datetime.datetime.fromisoformat(updated_at)
            except ValueError:
                # Fallback for other formats if necessary
                continue
                
        # Calculate time difference in hours
        diff = now - updated_at
        hours_passed = diff.total_seconds() / 3600
        
        if hours_passed >= todo["reminder_time"]:
            overdue.append(todo)
            
    return overdue

def update_todo_timestamp(conn, message_id, updated_at):
    cursor = conn.cursor()
    updated_at_str = updated_at.isoformat() if isinstance(updated_at, datetime.datetime) else updated_at
    cursor.execute("UPDATE todos SET updated_at = ? WHERE message_id = ?", (updated_at_str, message_id))
    conn.commit()

def get_updated_todos(conn):
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM todos WHERE updated_at != created_at")
    return cursor.fetchall()
