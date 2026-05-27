import discord
from discord.ext import commands, tasks
import datetime
from src.database.queries import (
    get_overdue_todos,
    get_channel_settings,
    update_todo_timestamp,
    delete_todo,
    get_updated_todos
)

class ReminderCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminder_loop.start()

    def cog_unload(self):
        self.reminder_loop.cancel()

    @tasks.loop(minutes=1.0)
    async def reminder_loop(self):
        await self.bot.wait_until_ready()
        
        # First, clear any todos that have been updated (i.e. updated_at != created_at)
        updated_todos = get_updated_todos(self.bot.db_conn)
        for todo in updated_todos:
            channel_id = todo["channel_id"]
            message_id = todo["message_id"]
            delete_todo(self.bot.db_conn, message_id)

        overdue_todos = get_overdue_todos(self.bot.db_conn)
        for todo in overdue_todos:
            channel_id = todo["channel_id"]
            message_id = todo["message_id"]
            user_id = todo["user_id"]
            
            settings = get_channel_settings(self.bot.db_conn, channel_id)
            if not settings:
                continue

            channel = self.bot.get_channel(channel_id)
            if not channel:
                continue

            thread = channel.get_thread(message_id)
            if not thread:
                # If thread was deleted or archived, we might not be able to get it this way.
                # If it's archived, we can try to fetch it:
                try:
                    thread = await channel.guild.fetch_channel(message_id)
                except discord.NotFound:
                    # Thread doesn't exist, we need to create it.
                    try:
                        original_msg = await channel.fetch_message(message_id)
                        base_name = f"{original_msg.content[:20]}..." if len(original_msg.content) > 20 else original_msg.content
                        thread_name = f"Reminder: {base_name}"
                        thread = await original_msg.create_thread(name=thread_name, auto_archive_duration=10080)
                    except discord.NotFound:
                        # Original message deleted, so we should untrack it
                        delete_todo(self.bot.db_conn, message_id)
                        continue
                    except discord.Forbidden:
                        continue
                except discord.Forbidden:
                    continue

            # Format the message
            user_mention = f"<@{user_id}>"
            message_link = f"https://discord.com/channels/{channel.guild.id}/{channel.id}/{message_id}"
            
            reminder_text = settings["reminder_message"]
            reminder_text = reminder_text.replace("{user}", user_mention)
            reminder_text = reminder_text.replace("{reminder_time}", str(todo["reminder_time"]))
            reminder_text = reminder_text.replace("{message_link}", message_link)

            try:
                await thread.send(reminder_text)
                # Update the timestamp so it doesn't spam every minute,
                # it will remind again after another reminder_time interval.
                update_todo_timestamp(self.bot.db_conn, message_id, datetime.datetime.now())
            except Exception as e:
                print(f"Failed to send reminder for {message_id}: {e}")

async def setup(bot):
    await bot.add_cog(ReminderCog(bot))
