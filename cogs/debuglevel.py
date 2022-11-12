import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import datetime
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
logger = logging.getLogger("debug")

formatter = logging.Formatter("[%(asctime)s] %(levelname)s:%(name)s: %(message)s",
                              "%Y-%m-%d %H:%M:%S")

file_handler = logging.FileHandler("main.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


class debug(commands.Cog):

   def __init__(self, bot : commands.Bot) -> None:
      self.bot  = bot
   
   @app_commands.command(
      name = "debuglevel",
      description = "Toggles the debug variable")
   @app_commands.describe(
        debuglevel = "debuglevel (`DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL`)"
    )

   async def debuglevel(self, interaction : discord.Interaction, debuglevel : str) -> None:
      await set_debug_level()
      debuglevel = debuglevel.upper()
      if interaction.user.id == 397046303378505729 or await self.check_permission(interaction.user.roles,ADMIN_ROLE_ID):
         if await self.update_json(debuglevel):
            msg = f"The `debuglevel` variable is set to {debuglevel}"
            logger.info(f"{interaction.user.name} changed debug to `{debuglevel}`")
         else:
            msg = f"`{debuglevel}` is not a valid option, please choose out: `DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL`"
            
         await interaction.response.send_message(msg, ephemeral=True)
      else:
         await interaction.response.send_message("You do not have the permission!", ephemeral=True)
         logger.info(f"{interaction.user.name} tried to use the `/debug` command")
   
   async def update_json(self, debuglevel : str):
      with path_json.open(mode="r+") as file:
         json_data = json.loads(file.read())
         if debuglevel == "DEBUG" or debuglevel == "INFO" or debuglevel == "WARNING" or debuglevel == "ERROR" or debuglevel == "CRITICAL":
            json_data["debuglevel"] = debuglevel
         else:
            return False
        
         file.seek(0)
         temp = json.dumps(json_data, indent=3)
         file.truncate(0)
         file.write(temp)
         return True
         
         
   async def check_permission(self, user_perms, needed_perm_id) -> bool: # Check if the user has a specific role
      for i in range(len(user_perms)):
         if user_perms[i].id == needed_perm_id:
               return True
      return False

async def setup(bot : commands.Bot) -> None:
   await bot.add_cog(
      debug(bot),
      guilds = [discord.Object(id = SERVER_ID)]
   )
   
   
async def set_debug_level():
    with path_json.open() as file:
        json_data = json.loads(file.read())
        debuglevel = json_data["debuglevel"]
    
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