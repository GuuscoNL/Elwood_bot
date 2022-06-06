import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv() # load all the variables from the env file
SERVER_ID =os.getenv('SERVER_ID')

class guus(commands.Cog):

   def __init__(self, bot : commands.Bot) -> None:
      self.bot  = bot
   
   @app_commands.command(
         name = "guus",
         description = "Gives an explanation and a video on how to pronounce Guus correctly")
   
   async def guus(self, interaction : discord.Interaction) -> None:
      explanation = "In Dutch, a G is pronounced quite like the German [ch], as in Bach. Or, while it doesn't exist in Standard English, you might also be familiar with this sound in Scottish words like “loch” and “ach.”"
      em = discord.Embed(title="How to pronounce Guus:", 
                            description=explanation )
      await interaction.response.send_message(embed= em)
      await interaction.channel.send("Video: https://www.youtube.com/watch?v=JsUJV2zvQtY")

async def setup(bot : commands.Bot) -> None:
   await bot.add_cog(
      guus(bot),
      guilds = [discord.Object(id = SERVER_ID)]
   )