import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import utils

load_dotenv() # load all the variables from the env file
SERVER_ID =os.getenv('SERVER_ID')

class guus(commands.Cog):

   def __init__(self, bot : commands.Bot) -> None:
      self.bot  = bot
      self.logger = bot.cog_loggers[self.__class__.__name__]
   
   @app_commands.command(
         name = "guus",
         description = "Gives an explanation and a video on how to pronounce Guus correctly")
   
   async def guus(self, interaction : discord.Interaction) -> None:
      utils.set_debug_level(self.logger)
      explanation = "In Dutch, a G is pronounced quite like the German [ch], as in Bach. Or, while it doesn't exist in Standard English, you might also be familiar with this sound in Scottish words like “loch” and “ach.”"
      await interaction.response.send_message(content=f"{explanation}\n\nVideo: https://www.youtube.com/watch?v=JsUJV2zvQtY", ephemeral=True)
      self.logger.info(f"{interaction.user.name} used the `/guus` command")
      
async def setup(bot : commands.Bot) -> None:
   await bot.add_cog(
      guus(bot),
      guilds = [discord.Object(id = SERVER_ID)]
   )
