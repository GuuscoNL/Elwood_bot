import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import json
import logging

load_dotenv() # load the variables needed from the .env file
SERVER_ID =os.getenv('SERVER_ID')
ADMIN_ROLE_ID = int(os.getenv('ADMIN_ROLE_ID'))

from pathlib import Path
path_dir = Path(__file__).parent.parent.resolve()
path_json = path_dir / "data.JSON"

#logging
logger = logging.getLogger("holiday_mode")

formatter = logging.Formatter("[%(asctime)s] %(levelname)-8s:%(name)-12s: %(message)s",
                              "%Y-%m-%d %H:%M:%S")

file_handler = logging.FileHandler("main.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

class holiday_mode(commands.Cog):

   def __init__(self, bot : commands.Bot) -> None:
      self.bot  = bot
   
   @app_commands.command(
      name = "holiday_mode",
      description = "Toggles the mode to holiday_mode or back to normal mode")

   @app_commands.checks.has_any_role(ADMIN_ROLE_ID) # Check if the author has the admin role. If not go to @toggle_server.error
   async def toggle_server(self, interaction : discord.Interaction) -> None:
      await set_debug_level()
      mode = await self.update_json()
      msg = f"Mode is set to {mode}"
      
      await interaction.response.send_message(msg, ephemeral=True)
      logger.info(f"{interaction.user.name} changed mode to {mode}")
      
   @toggle_server.error
   async def permission(self, interaction : discord.Interaction, error : app_commands.AppCommandError) -> None:
      if isinstance(error, app_commands.MissingAnyRole): # Check if the error is because of an missing role
         await set_debug_level()
         if interaction.user.id == 397046303378505729:# Check if the author is me (GuuscoNL)
            mode = await self.update_json()
            msg = f"Mode is set to {mode}"
            
            await interaction.response.send_message(msg, ephemeral=True)
            logger.info(f"{interaction.user.name} changed mode to {mode}")
         else:
            await interaction.response.send_message("You do not have the permission!", ephemeral=True)
            logger.info(f"{interaction.user.name} tried to use the `/holiday_mode` command") # Log it
   
   async def update_json(self):
      with path_json.open(mode="r+") as file:
         json_data = json.loads(file.read())
         if json_data["mode"] == 2:
            json_data["mode"] = 1
         else:
            json_data["mode"] = 2
         file.seek(0)
         temp = json.dumps(json_data, indent=3)
         file.truncate(0)
         file.write(temp)
      return json_data["mode"]

async def setup(bot : commands.Bot) -> None:
   await bot.add_cog(
      holiday_mode(bot),
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