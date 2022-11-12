import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import logging
import os
import json

load_dotenv() # load all the variables from the env file
SERVER_ID =os.getenv('SERVER_ID')

from pathlib import Path
path_dir = Path(__file__).parent.parent.resolve()
path_json = path_dir / "data.JSON"

#logging
logger = logging.getLogger("content")

formatter = logging.Formatter("[%(asctime)s] %(levelname)s:%(name)s: %(message)s",
                              "%Y-%m-%d %H:%M:%S")

file_handler = logging.FileHandler("main.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

class content(commands.Cog):

    def __init__(self, bot : commands.Bot) -> None:
        self.bot  = bot
    
    @app_commands.command(
        name = "content",
        description = "Gives a link to the Steam Workshop collection that the TBN server uses")

    async def content(self, interaction : discord.Interaction) -> None:
        
        mesg = """The Content for the server is NOT REQUIRED.
It is FASTER, to join the server without it.
Only Subscribe to the server if your problems persist after a restart of the game and joining the server again.
\n||https://steamcommunity.com/workshop/filedetails/?id=2566173658||"""
        logger.info(f"{interaction.user.name} used the `/content` command")
        await interaction.response.send_message(mesg, ephemeral=True)

async def setup(bot : commands.Bot) -> None:
    await bot.add_cog(
        content(bot),
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