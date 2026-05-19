import discord
from discord.ext import commands
from discord import app_commands
from src.database.queries import set_channel_settings

class SetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup", description="Run an interactive setup for a todo-list channel")
    @app_commands.default_permissions(manage_channels=True)
    @app_commands.describe(
        channel="The channel to track todos in",
        reminder_time="Hours before a reminder is sent (default: 24)",
        reminder_message="Template for the reminder message",
        completion_reaction="Emoji used to mark a todo as complete (default: ✅)"
    )
    async def setup(
        self, 
        interaction: discord.Interaction, 
        channel: discord.TextChannel,
        reminder_time: int = 24,
        reminder_message: str = "{user} hasn't updated their todo in {reminder_time} hours: {message_link}",
        completion_reaction: str = "✅"
    ):
        set_channel_settings(
            self.bot.db_conn,
            channel.id,
            reminder_time,
            reminder_message,
            completion_reaction
        )
        await interaction.response.send_message(
            f"✅ Setup complete for {channel.mention}!\n"
            f"**Reminder Time**: {reminder_time} hours\n"
            f"**Reminder Message**: `{reminder_message}`\n"
            f"**Completion Reaction**: {completion_reaction}",
            ephemeral=True
        )

    @app_commands.command(name="set_channel", description="Set the current channel as a todo-list channel")
    @app_commands.default_permissions(manage_channels=True)
    async def set_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        set_channel_settings(self.bot.db_conn, channel.id)
        await interaction.response.send_message(f"✅ Set {channel.mention} as a todo list channel.", ephemeral=True)

    @app_commands.command(name="clear_channel", description="Clear a todo-list channel (stops tracking)")
    @app_commands.default_permissions(manage_channels=True)
    async def clear_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        # We can implement 'clearing' by removing it from settings or just setting a flag.
        # Since I didn't create a delete_channel_settings query, I'll execute it directly here or just add one.
        cursor = self.bot.db_conn.cursor()
        cursor.execute("DELETE FROM channel_settings WHERE channel_id = ?", (channel.id,))
        self.bot.db_conn.commit()
        await interaction.response.send_message(f"✅ Cleared todo list settings for {channel.mention}.", ephemeral=True)

    @app_commands.command(name="set_reminder_time", description="Set the reminder interval for a channel in hours")
    @app_commands.default_permissions(manage_channels=True)
    async def set_reminder_time(self, interaction: discord.Interaction, channel: discord.TextChannel, hours: int):
        set_channel_settings(self.bot.db_conn, channel.id, reminder_time=hours)
        await interaction.response.send_message(f"✅ Reminder time for {channel.mention} set to {hours} hours.", ephemeral=True)

    @app_commands.command(name="set_reminder_message", description="Set the reminder message template")
    @app_commands.default_permissions(manage_channels=True)
    async def set_reminder_message(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str):
        set_channel_settings(self.bot.db_conn, channel.id, reminder_message=message)
        await interaction.response.send_message(f"✅ Reminder message for {channel.mention} set to:\n`{message}`", ephemeral=True)

    @app_commands.command(name="set_completion_reaction", description="Set the completion reaction for a channel")
    @app_commands.default_permissions(manage_channels=True)
    async def set_completion_reaction(self, interaction: discord.Interaction, channel: discord.TextChannel, reaction: str):
        set_channel_settings(self.bot.db_conn, channel.id, completion_reaction=reaction)
        await interaction.response.send_message(f"✅ Completion reaction for {channel.mention} set to: {reaction}", ephemeral=True)

    @app_commands.command(name="help", description="Display the help message for Todo Reminder Bot")
    async def help_cmd(self, interaction: discord.Interaction):
        help_text = (
            "**Todo Reminder Bot Help**\n\n"
            "This bot tracks todos in specified channels and sends reminders in threads if they are not updated.\n\n"
            "**Commands (require Manage Channels):**\n"
            "`/setup` - Interactive setup for a channel.\n"
            "`/set_channel` - Designate a channel for todos.\n"
            "`/clear_channel` - Stop tracking a channel.\n"
            "`/set_reminder_time` - Set how many hours before a reminder is sent.\n"
            "`/set_reminder_message` - Set the text of the reminder.\n"
            "`/set_completion_reaction` - Set the emoji used to complete a todo.\n\n"
            "**How to use:**\n"
            "1. Setup a channel using `/setup`.\n"
            "2. Users post a todo message in that channel.\n"
            "3. The bot will silently track the message in the background.\n"
            "4. If the original message isn't updated (edited) or marked as complete before the reminder time elapses, a thread is created and a reminder is sent.\n"
            "5. To complete a todo, react to the original message with the completion emoji (default ✅).\n\n"
            "**Message Template Placeholders:**\n"
            "When setting a custom reminder message, use these placeholders:\n"
            "`{user}` - Pings the original poster.\n"
            "`{reminder_time}` - Shows the reminder interval in hours.\n"
            "`{message_link}` - Provides a clickable link to the todo."
        )
        await interaction.response.send_message(help_text, ephemeral=True)

async def setup(bot):
    await bot.add_cog(SetupCog(bot))
