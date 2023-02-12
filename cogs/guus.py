import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import json
import logging

load_dotenv() # load all the variables from the env file
SERVER_ID =os.getenv('SERVER_ID')

from pathlib import Path
path_dir = Path(__file__).parent.parent.resolve()
path_json = path_dir / "data.JSON"

#logging
logger = logging.getLogger("guus")

formatter = logging.Formatter("[%(asctime)s] %(levelname)-8s:%(name)-12s: %(message)s",
                              "%Y-%m-%d %H:%M:%S")

file_handler = logging.FileHandler("main.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

class guus(commands.Cog):

   def __init__(self, bot : commands.Bot) -> None:
      self.bot  = bot
   
   @app_commands.command(
         name = "guus",
         description = "Gives an explanation and a video on how to pronounce Guus correctly")
   
   async def guus(self, interaction : discord.Interaction) -> None:
      await set_debug_level()
      explanation = "In Dutch, a G is pronounced quite like the German [ch], as in Bach. Or, while it doesn't exist in Standard English, you might also be familiar with this sound in Scottish words like “loch” and “ach.”"
      await interaction.response.send_message(content=f"{explanation}\n\nVideo: https://www.youtube.com/watch?v=JsUJV2zvQtY", ephemeral=True)
      logger.info(f"{interaction.user.name} used the `/guus` command")
      
async def setup(bot : commands.Bot) -> None:
   await bot.add_cog(
      guus(bot),
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