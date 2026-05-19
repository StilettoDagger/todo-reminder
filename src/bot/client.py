import discord
from discord.ext import commands

class TodoBot(commands.Bot):
    def __init__(self, db_conn):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        intents.guilds = True
        super().__init__(command_prefix="!", intents=intents)
        self.db_conn = db_conn

    async def setup_hook(self):
        # We will load cogs here
        await self.load_extension('src.bot.cogs.setup_cog')
        await self.load_extension('src.bot.cogs.todo_cog')
        await self.load_extension('src.bot.cogs.reminder_cog')
        
        # Sync slash commands
        await self.tree.sync()
        
    async def on_ready(self):
        print(f"Logged in as {self.user.name} ({self.user.id})")
