import discord
import datetime
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv() # load all the variables from the env file
SERVER_ID = os.getenv('SERVER_ID')

class stardate(commands.Cog):

   def __init__(self, bot : commands.Bot) -> None:
      self.bot  = bot
   
   @app_commands.command(
      name = "stardate",
      description = "Get the current date converted to a stardate (year 2382)")
   
   async def stardate(self, interaction : discord.Interaction) -> None:
      b = 2323 # reference earthdate
      c = 0 # reference stardate

      t = datetime.datetime.now().timetuple() # Get current time
      year = t.tm_year + 359 # convert current year to correct year (2022 = 2381, so + 359)

      if year % 400 == 0 or (year % 4 == 0 and year % 100 != 0): #check if leap year
            n = 366
      else:
            n = 365

      result = format(((c + (1000*(year - b))) +
                           ((1000/((n)*1440.0))*(((
                           t.tm_yday - 1.0)*1440.0) +
                           (t.tm_hour*60.0) + t.tm_min))), '.2f')
      await interaction.response.send_message(f"Current stardate is {result}", ephemeral=True)


async def setup(bot : commands.Bot) -> None:
   await bot.add_cog(
      stardate(bot),
      guilds = [discord.Object(id = SERVER_ID)]
   )