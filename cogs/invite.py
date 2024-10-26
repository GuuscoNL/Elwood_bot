import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import utils

load_dotenv() # load all the variables from the env file
SERVER_ID =os.getenv('SERVER_ID')

class invite(commands.Cog):

   def __init__(self, bot : commands.Bot) -> None:
      self.bot  = bot
      self.logger = bot.cog_loggers[self.__class__.__name__]
   
   @app_commands.command(
      name = "invite",
      description = "Sends an invite link that you can share with people")
   
   async def invite(self, interaction : discord.Interaction) -> None:
      utils.set_debug_level(self.logger)
      await interaction.response.send_message(f"Send this link to people you would like to invite to this server: https://discord.com/invite/5zTdXs4yJu", ephemeral=True)
      self.logger.info(f"{interaction.user.name} used the `/invite` command")


async def setup(bot : commands.Bot) -> None:
   await bot.add_cog(
      invite(bot),
      guilds = [discord.Object(id = SERVER_ID)]
   )