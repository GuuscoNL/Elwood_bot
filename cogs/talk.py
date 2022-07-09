import discord
import datetime
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv() # load all the variables from the env file
SERVER_ID = os.getenv('SERVER_ID')
ADMIN_ROLE_ID = int(os.getenv('ADMIN_ROLE_ID'))

class talk(commands.Cog):

    def __init__(self, bot : commands.Bot) -> None:
        self.bot  = bot
    
    @app_commands.command(
        name = "talk",
        description = "Makes the bot talk")
    @app_commands.describe(
        text = "text"
    )

    # ---------------- I knew you would look Poe! ---------------- 
    
    @app_commands.checks.has_any_role(ADMIN_ROLE_ID) # Check if the author has the admin role. If not go to @talk.error
    async def talk(self, interaction : discord.Interaction, text : str) -> None:
        await interaction.response.send_message(content=f"Saying:\n> {text}", ephemeral=True)
        await interaction.channel.send(content=text)
        print(f"[{await self.current_time()}] {interaction.user.name} used the talk command and said: \"{text}\"")
        
    @talk.error
    async def permission(self, interaction : discord.Interaction, error : app_commands.AppCommandError, text : str) -> None:
        if isinstance(error, app_commands.MissingAnyRole): # Check if the error is because of an missing role
            if interaction.user.id == 397046303378505729:# Check if the author is me (GuuscoNL)
                await interaction.response.send_message(content=f"Saying:\n> {text}", ephemeral=True)
                await interaction.channel.send(content=text)
                print(f"[{await self.current_time()}] {interaction.user.name} used the talk command and said: \"{text}\"")
            else:
                await interaction.response.send_message("You do not have the permission!", ephemeral=True)
                print(f"[{await self.current_time()}] {interaction.user.name} tried to use the `/talk` command")

    async def current_time(self): # Get current time
      now = datetime.datetime.utcnow()
      return now.strftime("%d/%m/%Y %H:%M:%S UTC")

async def setup(bot : commands.Bot) -> None:
    await bot.add_cog(
        talk(bot),
        guilds = [discord.Object(id = SERVER_ID)]
    )