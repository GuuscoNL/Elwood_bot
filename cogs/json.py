import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import time
import json
import logging

load_dotenv() # load the variables needed from the .env file
SERVER_ID = os.getenv('SERVER_ID')
ADMIN_ROLE_ID = int(os.getenv('ADMIN_ROLE_ID'))

from pathlib import Path
path_dir = Path(__file__).parent.parent.resolve()
path_json = path_dir / "data.JSON"

#logging
logger = logging.getLogger("json")

formatter = logging.Formatter("[%(asctime)s] %(levelname)-8s:%(name)-12s: %(message)s",
                              "%d-%m-%Y %H:%M:%S")
formatter.converter = time.gmtime

file_handler = logging.FileHandler("main.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

class command_json(commands.Cog):

   def __init__(self, bot : commands.Bot) -> None:
      self.bot  = bot
   
   @app_commands.command(
      name = "json",
      description = "Shows what the json file contains")

   @app_commands.checks.has_any_role(ADMIN_ROLE_ID) # Check if the author has the admin role. If not go to @json.error
   async def command_json(self, interaction : discord.Interaction) -> None:
      await set_debug_level()
      with path_json.open(mode="r") as file:
         json_data = json.loads(file.read())   
      await interaction.response.send_message(f"```{json_data}```", ephemeral=True)
      logger.info(f"{interaction.user.name} used the `/json` command")
      
   @command_json.error
   async def permission(self, interaction : discord.Interaction, error : app_commands.AppCommandError) -> None:
      if isinstance(error, app_commands.MissingAnyRole): # Check if the error is because of an missing role
         await set_debug_level()
         if interaction.user.id == 397046303378505729:# Check if the author is me (GuuscoNL)
               with path_json.open(mode="r") as file:
                  json_data = json.loads(file.read())
               await interaction.response.send_message(f"```{json_data}```", ephemeral=True)
               logger.info(f"{interaction.user.name} used the `/json` command")
         else:
               await interaction.response.send_message("You do not have permission to use this command!", ephemeral=True)
               logger.warning(f"{interaction.user.name} tried to use `/json`")

async def setup(bot : commands.Bot) -> None:
   await bot.add_cog(
      command_json(bot),
      guilds = [discord.Object(id = SERVER_ID)]
   )
   
async def set_debug_level():
    with path_json.open() as file:
        json_data = json.loads(file.read())
        debuglevel = json_data["loglevel"]
    
    if debuglevel == "DEBUG":
        logger.setLevel(logging.DEBUG)
    elif debuglevel == "INFO":
        logger.setLevel(logging.INFO)
    elif debuglevel == "WARNING":
        logger.setLevel(logging.WARNING)
    elif debuglevel == "ERROR":
        logger.setLevel(logging.ERROR)
    elif debuglevel == "CRITICAL":
        logger.setLevel(logging.CRITICAL)
    else:
        print("no debug level set")
        logger.setLevel(logging.NOTSET)