import discord
import datetime
import time
from dateutil.relativedelta import relativedelta
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import json
import logging

load_dotenv() # load all the variables from the env file
SERVER_ID = os.getenv('SERVER_ID')

from pathlib import Path
path_dir = Path(__file__).parent.parent.resolve()
path_json = path_dir / "data.JSON"

#logging
logger = logging.getLogger("earthdate")

formatter = logging.Formatter("[%(asctime)s] %(levelname)-8s:%(name)-12s: %(message)s",
                              "%Y-%m-%d %H:%M:%S")

file_handler = logging.FileHandler("main.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

class earthdate(commands.Cog):

   def __init__(self, bot : commands.Bot) -> None:
      self.bot  = bot
   
   @app_commands.command(
      name = "earthdate",
      description = "Convert a stardate to a normal date")
   @app_commands.describe(
        stardate = "earthdate"
    )
   async def stardate(self, interaction : discord.Interaction, stardate : str) -> None:
      await set_debug_level()
      try:
         stardate = float(stardate)
         date = await stardate_to_date(stardate)
         unix_time = time.mktime(date.timetuple())
         await interaction.response.send_message(f"The date on that stardate is <t:{int(unix_time)}:D>\nTo calculate a custom stardate use this website: https://guusconl.github.io/TBN.github.io/", ephemeral=True, suppress_embeds=True)
         logger.info(f"{interaction.user.name} used the `/earthdate` command")
      except ValueError:
         await interaction.response.send_message(f"Please put a stardate as input, like: `59947.891`", ephemeral=True, suppress_embeds=True)
         logger.info(f"{interaction.user.name} Tried to use the `/earthdate` command")

async def stardate_to_date(stardate) -> datetime:
   StarTime = stardate
   
   earthdate = (StarTime / 1000) + 2323
   earthdates = str(earthdate) + ".0"
   vector = earthdates.split(".")
   year = int(vector[0])
   frag_year = float("0." + vector[1])
   if year % 400 == 0 or (year % 4 == 0 and year % 100 != 0):
       xday = 366
   else:
       xday = 365
   if (frag_year == 0):
       return datetime.datetime(year=year, month=1, day=1, hour=0, minute=0, second=0)
   else:
      days = int((frag_year * xday) % xday)
      hour = int((frag_year * 24 * xday) % 24)
      min = int((frag_year * 1440 * xday) % 60)
      sec = int((frag_year * 86400 * xday) % 60)
      date = datetime.datetime(year=year, month=1, day=1, hour=hour, minute=min, second=sec)
      date = date + relativedelta(days=days)
      return date

async def setup(bot : commands.Bot) -> None:
   await bot.add_cog(
      earthdate(bot),
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