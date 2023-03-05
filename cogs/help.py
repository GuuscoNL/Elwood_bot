import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import time
import logging
import json

from pathlib import Path
path_dir = Path(__file__).parent.parent.resolve()
path_rank_json = path_dir / "rank_data.JSON"
path_json = path_dir / "data.JSON"

JSON_DATA = None
rank_permission_roles = []
with path_rank_json.open() as file:
    JSON_DATA = json.loads(file.read())
    for role_id, _ in JSON_DATA["promotion_perms"].items():
        rank_permission_roles.append(int(role_id))

#logging
logger = logging.getLogger("help")

formatter = logging.Formatter("[%(asctime)s] %(levelname)-8s:%(name)-12s: %(message)s",
                              "%d-%m-%Y %H:%M:%S")
formatter.converter = time.gmtime

file_handler = logging.FileHandler("main.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

load_dotenv() # load all the variables from the env file
SERVER_ID =os.getenv('SERVER_ID')
ADMIN_ROLE_ID = int(os.getenv('ADMIN_ROLE_ID'))

class help(commands.Cog):

   def __init__(self, bot : commands.Bot) -> None:
      self.bot  = bot
   
   @app_commands.command(
      name = "help",
      description = "Gives a list of all available commands")
    
   @app_commands.checks.has_any_role(ADMIN_ROLE_ID) # Check if the author has the admin role. If not go to @help.error
   async def help(self, interaction : discord.Interaction) -> None:
      await set_debug_level()
      em = discord.Embed(title="Elwood commands:")
      em = await self.help_admin(em)
      em = await self.help_public(em)
      em = await self.help_special(em, interaction.user.roles)
      await interaction.response.send_message(embed=em, ephemeral=True)
      logger.info(f"{interaction.user.name} used the `/help` command")
      
   @help.error
   async def permission(self, interaction : discord.Interaction, error : app_commands.AppCommandError) -> None:  
      if isinstance(error, app_commands.MissingAnyRole): # Check if the error is because of an missing role
         await set_debug_level()
         if interaction.user.id == 397046303378505729: # Check if the author is me (GuuscoNL)
            em = discord.Embed(title="Elwood commands:")
            em = await self.help_admin(em)
            await interaction.response.send_message(embed= await self.help_public(em), ephemeral=True)
         else:
            em = discord.Embed(title="Elwood commands:")
            await interaction.response.send_message(embed= await self.help_public(em), ephemeral=True)
         logger.info(f"{interaction.user.name} used the `/help` command")
   
   async def help_public(self, em : discord.Embed):
      public_help = '''`/help`
      Gives a list of all the commands and what they do
      
      `/content`
      Gives a link to Steam Workshop collection with all the content packs you need for the TBN server
      
      `/roll`
      Roll between 0 and 100
      
      `/invite`
      Get an invite link that you can share with people
      
      `/guus`
      Gives an explanation and a video on how to pronounce Guus correctly
      
      `/stardate`
      Get the current date converted to a stardate
      
      `/earthdate`
      Convert a stardate to a normal date with a 24 hour accuracy
      '''
      em.add_field(name="Public commands:", value=public_help)
      return em
   
   async def help_special(self, em : discord.Embed, roles: list[discord.Role]):
      public_help = ""
      
      if await self.check_permission_any(roles, rank_permission_roles):
         public_help += "`/rank`\nPromote or demote users. Perms are based on role\n\n"
      
      if public_help != "":
         em.add_field(name="Special commands:", value=public_help)
         
      return em
   
   async def help_admin(self, em : discord.Embed):
      admin_help = '''`/ping`
      Pings the bot
      
      `/restart`
      Restarts the bot
      
     `/json`
      Shows what is in the data.JSON file
      
      `/holiday_mode`
      Toggles the mode to holiday_mode or back to normal mode
      
      `/loglevel`
      Set the loglevel
      
      `/sleep_mode`
      Toggles the mode to sleep_mode or back to normal mode
      
      `/talk`
      Makes the bot talk in the current channel. Put the text you want the bot to say in the text parameter
      
      `/log`
      Shows the bots logs
      '''
      em.add_field(name="Admin commands:", value=admin_help)
      return em
   
   async def check_permission_any(self, user_perms: list[discord.Role], needed_perms: list[int]) -> bool: # Check if the user has a specific role
        for i in range(len(user_perms)):
            if user_perms[i].id in needed_perms:
                return True
        return False

async def setup(bot : commands.Bot) -> None:
   await bot.add_cog(
      help(bot),
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