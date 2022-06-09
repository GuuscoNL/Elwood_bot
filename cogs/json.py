import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import json

load_dotenv() # load the variables needed from the .env file
SERVER_ID =os.getenv('SERVER_ID')
ADMIN_ROLE_ID =os.getenv('ADMIN_ROLE_ID')

from pathlib import Path
path_dir = Path(__file__).parent.parent.resolve()
path_json = path_dir / "data.JSON"

class command_json(commands.Cog):

   def __init__(self, bot : commands.Bot) -> None:
      self.bot  = bot
   
   @app_commands.command(
      name = "json",
      description = "Shows what the json file contains")

   @app_commands.checks.has_any_role(ADMIN_ROLE_ID) # Check if the author has the admin role. If not go to @json.error
   async def command_json(self, interaction : discord.Interaction) -> None:
      with path_json.open(mode="r") as file:
         json_data = json.loads(file.read())   
      await interaction.response.send_message(f"```{json_data}```")
      
   @command_json.error
   async def permission(self, interaction : discord.Interaction, error : app_commands.AppCommandError) -> None:
      if isinstance(error, app_commands.MissingAnyRole): # Check if the error is because of an missing role
         if interaction.user.id == 397046303378505729:# Check if the author is me (GuuscoNL)
               with path_json.open(mode="r") as file:
                  json_data = json.loads(file.read())
               await interaction.response.send_message(f"```{json_data}```")
         else:
               await interaction.response.send_message("You do not have the permission!", ephemeral=True)

async def setup(bot : commands.Bot) -> None:
   await bot.add_cog(
      command_json(bot),
      guilds = [discord.Object(id = SERVER_ID)]
   )