import discord
from discord.ext import commands
import datetime
from src.database.queries import (
    get_channel_settings,
    add_todo,
    get_todo_by_message_id,
    delete_todo
)

class TodoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # Check if the channel is a todo channel
        settings = get_channel_settings(self.bot.db_conn, message.channel.id)
        if not settings:
            return

        try:
            # Insert into database
            now = datetime.datetime.now()
            add_todo(
                self.bot.db_conn,
                channel_id=message.channel.id,
                message_id=message.id,
                user_id=message.author.id,
                created_at=now,
                updated_at=now,
                reminder_time=settings["reminder_time"]
            )
        except Exception as e:
            print(f"Failed to track todo: {e}")

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if after.author.bot:
            return

        todo = get_todo_by_message_id(self.bot.db_conn, after.id)
        if todo:
            delete_todo(self.bot.db_conn, after.id)
            
            try:
                await after.add_reaction("⭐")
            except (discord.Forbidden, discord.HTTPException):
                pass
            
            channel = self.bot.get_channel(todo["channel_id"])
            if channel:
                # Get the thread (thread ID is usually the message ID)
                thread = channel.get_thread(after.id)
                if thread:
                    # Archive the thread since reminders are stopped
                    await thread.edit(archived=True)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        todo = get_todo_by_message_id(self.bot.db_conn, payload.message_id)
        if todo:
            delete_todo(self.bot.db_conn, payload.message_id)

async def setup(bot):
    await bot.add_cog(TodoCog(bot))
