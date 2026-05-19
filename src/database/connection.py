def initialize_db(conn):
    cursor = conn.cursor()
    
    # Create todos table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel_id INTEGER,
        message_id INTEGER,
        user_id INTEGER,
        created_at DATETIME,
        updated_at DATETIME,
        reminder_time INTEGER
    )
    ''')
    
    # Create channel_settings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS channel_settings (
        channel_id INTEGER PRIMARY KEY,
        reminder_time INTEGER DEFAULT 24,
        reminder_message TEXT DEFAULT '{user} hasn''t updated their todo in {reminder_time} hours: {message_link}',
        completion_reaction TEXT DEFAULT '✅'
    )
    ''')
    
    conn.commit()
