import discord
from discord import app_commands
from discord.ext import commands
import random as rnd
from dotenv import load_dotenv
import os
import utils

load_dotenv() # load all the variables from the env file
SERVER_ID = os.getenv('SERVER_ID')


class roll(commands.Cog):

   def __init__(self, bot : commands.Bot) -> None:
      self.bot  = bot
      self.logger = bot.cog_loggers[self.__class__.__name__]
   
   @app_commands.command(
      name = "roll",
      description = "Rolls between 0 and 100")
   async def roll(self, interaction : discord.Interaction) -> None:
      utils.set_debug_level(self.logger)
      roll = rnd.randint(0,100)
      if roll == 0:
         await interaction.response.send_message(f"You rolled a {roll}, have you thought of joining medical?")
      elif roll == 100:
         await interaction.response.send_message(f"You rolled a {roll}, wow...")
      elif roll == 69:
         await interaction.response.send_message(f"You rolled a {roll}, nice")
      else:
         await interaction.response.send_message(f"You rolled a {roll}")
      self.logger.info(f"{interaction.user.name} used the `/roll` command ({roll})")

async def setup(bot : commands.Bot) -> None:
   await bot.add_cog(
      roll(bot),
      guilds = [discord.Object(id = SERVER_ID)]
   )