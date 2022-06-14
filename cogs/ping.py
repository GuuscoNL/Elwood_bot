import discord
import datetime
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv() # load all the variables from the env file
SERVER_ID = os.getenv('SERVER_ID')
ADMIN_ROLE_ID = int(os.getenv('ADMIN_ROLE_ID'))

class ping(commands.Cog):

    def __init__(self, bot : commands.Bot) -> None:
        self.bot  = bot
    
    @app_commands.command(
        name = "ping",
        description = "Pings the bot")

    @app_commands.checks.has_any_role(ADMIN_ROLE_ID) # Check if the author has the admin role. If not go to @ping.error
    async def ping(self, interaction : discord.Interaction) -> None:
        await interaction.response.send_message(f"pong ({str(self.bot.latency*1000)[0:6]} ms)", ephemeral=True)
        print(f"[{await self.current_time()}] {interaction.user.name} pinged the bot")
        
    @ping.error
    async def permission(self, interaction : discord.Interaction, error : app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.MissingAnyRole): # Check if the error is because of an missing role
            if interaction.user.id == 397046303378505729:# Check if the author is me (GuuscoNL)
                await interaction.response.send_message(f"pong ({str(self.bot.latency*1000)[0:6]} ms)", ephemeral=True)
                print(f"[{await self.current_time()}] {interaction.user.name} pinged the bot")
            else:
                await interaction.response.send_message("You do not have the permission!", ephemeral=True)
                print(f"[{await self.current_time()}] {interaction.user.name} tried to use the `/ping` command")
    
    async def current_time(self): # Get current time
      now = datetime.datetime.utcnow()
      return now.strftime("%d/%m/%Y %H:%M:%S UTC")

async def setup(bot : commands.Bot) -> None:
    await bot.add_cog(
        ping(bot),
        guilds = [discord.Object(id = SERVER_ID)]
    )