import sqlite3
import os
from src.config import DISCORD_TOKEN, DATABASE_PATH
from src.database.connection import initialize_db
from src.bot.client import TodoBot

def main():
    if not DISCORD_TOKEN:
        print("Error: DISCORD_TOKEN environment variable not set.")
        return

    # Ensure data directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    # Initialize database
    conn = sqlite3.connect(DATABASE_PATH)
    initialize_db(conn)

    # Initialize and run bot
    bot = TodoBot(db_conn=conn)
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()
