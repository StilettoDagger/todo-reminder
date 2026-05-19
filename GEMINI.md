## Project guidelines

### Language requirements

- Use latest stable version of Python
- Use sqlite3 for the database
- Use a python virtual environment for dependencies

### Project requirements

- Create a discord bot that alerts users about their overdue todos in certain channels
  - The bot should create a thread for each todo message to post reminders
  - The reminders should be sent if the original todo message hasn't been updated for the set reminder time
  - The reminder message can be customized and may include the name of the user who posted the todo, and a link to the todo message.
  - The bot should no longer send reminders if the todo is completed or the original todo message is deleted
  - There should be a way to mark a todo as completed using the bot (maybe a reaction to the todo message?)
  - All reminders should be sent in the thread
- Create a database for storing reminder information
- The bot should have the following commands:
  - /setup: Run an interactive setup for the bot:
    - Ask for the todo-list channel
    - Ask for the reminder interval in hours
    - Ask for the reminder message template
    - Set channel(s) where the bot should post reminders
  - /set_channel: Set the todo-list channel where the bot should create threads
  - /clear_channel: Clear the todo-list channel
  - /set_reminder_time: Set the reminder interval for a channel in hours (default: 24 hours)
  - /set_reminder_message: Set the reminder message template (default: "{user} hasn't updated their todo in {reminder_time} hours: {message_link}")
  - /help: Display the help message

### Database schema

- Create a table called todos with the following columns:
  - id: Integer primary key
  - channel_id: Integer
  - message_id: Integer
  - user_id: Integer
  - created_at: DateTime
  - updated_at: DateTime
  - reminder_time: Integer


### Project workflow

- Use git for version control. Make sure you commit your changes frequently with useful commit messages and use branches for new features.
- Use incremental builds, if a feature is not working as expected, fix it before moving on
- Use test-driven development, write tests before writing the code.
- Modularize your code, create separate files for different functionalities and keep things organized in approrpriate folders.
- Document your code, add comments and docstrings.
- Make sure the bot is well-documented and easy to use.
