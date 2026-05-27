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
    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
        # We only care if the message is a tracked todo
        todo = get_todo_by_message_id(self.bot.db_conn, payload.message_id)
        if not todo:
            return

        # Check if this was a user edit (has edited_timestamp) rather than an automatic embed update
        # If the bot lacks the Message Content intent, 'content' won't be present, but 'edited_timestamp' will be.
        if "edited_timestamp" not in payload.data and "content" not in payload.data:
            return

        # Get or fetch the channel
        channel = self.bot.get_channel(payload.channel_id)
        if not channel:
            try:
                channel = await self.bot.fetch_channel(payload.channel_id)
            except discord.HTTPException:
                return

        # Fetch the updated message
        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.HTTPException:
            return

        if message.author.bot:
            return

        # If the message was cached, double check the edit time or content changed
        if payload.cached_message:
            # If both the edit timestamp and content are the same, it wasn't a real user edit
            if payload.cached_message.edited_at == message.edited_at and payload.cached_message.content == message.content:
                return

        # Delete the todo to mark it as completed
        delete_todo(self.bot.db_conn, payload.message_id)

        try:
            await message.add_reaction("⭐")
        except (discord.Forbidden, discord.HTTPException):
            pass

        # Archive the thread if possible
        if hasattr(channel, 'get_thread'):
            thread = channel.get_thread(payload.message_id)
            if thread:
                try:
                    await thread.edit(archived=True, reason="Todo completed")
                except discord.HTTPException:
                    pass

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        todo = get_todo_by_message_id(self.bot.db_conn, payload.message_id)
        if todo:
            delete_todo(self.bot.db_conn, payload.message_id)

async def setup(bot):
    await bot.add_cog(TodoCog(bot))
