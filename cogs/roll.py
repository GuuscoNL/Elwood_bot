import discord
from discord import app_commands
from discord.ext import commands
import random as rnd
from dotenv import load_dotenv
import os
import time
import json
import logging

load_dotenv() # load all the variables from the env file
SERVER_ID = os.getenv('SERVER_ID')

from pathlib import Path
path_dir = Path(__file__).parent.parent.resolve()
path_json = path_dir / "data.JSON"

#logging
logger = logging.getLogger("roll")

formatter = logging.Formatter("[%(asctime)s] %(levelname)-8s:%(name)-12s: %(message)s",
                              "%d-%m-%Y %H:%M:%S")
formatter.converter = time.gmtime

file_handler = logging.FileHandler("main.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

class roll(commands.Cog):

   def __init__(self, bot : commands.Bot) -> None:
      self.bot  = bot
   
   @app_commands.command(
      name = "roll",
      description = "Rolls between 0 and 100")
   async def roll(self, interaction : discord.Interaction) -> None:
      await set_debug_level()
      roll = rnd.randint(0,100)
      if roll == 0:
         await interaction.response.send_message(f"You rolled a {roll}, have you thought of joining medical?")
      elif roll == 100:
         await interaction.response.send_message(f"You rolled a {roll}, wow...")
      elif roll == 69:
         await interaction.response.send_message(f"You rolled a {roll}, nice")
      else:
         await interaction.response.send_message(f"You rolled a {roll}")
      logger.info(f"{interaction.user.name} used the `/roll` command ({roll})")

async def setup(bot : commands.Bot) -> None:
   await bot.add_cog(
      roll(bot),
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