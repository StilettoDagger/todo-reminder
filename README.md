# Todo Reminder Discord Bot

A Discord bot that automatically tracks todos in designated channels and reminds users if they haven't updated them.

## Features
- Tracks new messages in specified channels and creates threads for them automatically.
- Sends reminders in the threads if the todo hasn't been updated for a set number of hours.
- Customizable reminder intervals, messages, and completion reactions per channel.
- Uses Test-Driven Development (TDD) with `pytest`.
- Built with `discord.py` and `sqlite3`.

## Setup

1. **Install Dependencies:**
   Create a virtual environment and install the required packages:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   Create a `.env` file in the root directory and add your Discord Bot Token:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   ```

3. **Run the Bot:**
   ```bash
   python todo-reminder.py
   ```

## Usage

In Discord, an admin (with "Manage Channels" permission) can use the following slash commands:
- `/setup`: Interactive setup for a channel (sets channel, reminder interval, message, and reaction).
- `/set_channel`: Designate a channel for todos.
- `/clear_channel`: Stop tracking a channel.
- `/set_reminder_time`: Set how many hours before a reminder is sent.
- `/set_reminder_message`: Set the text of the reminder.
- `/set_completion_reaction`: Set the emoji used to complete a todo.
- `/help`: Display the help message.

### Working with Todos
- Post a message in a tracked channel to create a todo. The bot will automatically start a thread.
- If the original message isn't edited or the thread isn't updated within the reminder time, the bot sends a reminder in the thread.
- To complete a todo, react to the original message with the completion emoji (default ✅). This stops further reminders.

## Testing
Run tests using `pytest`:
```bash
PYTHONPATH=. pytest tests/
```
