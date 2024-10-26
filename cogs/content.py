import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import logging
import os
import time

import utils

load_dotenv() # load all the variables from the env file
SERVER_ID =os.getenv('SERVER_ID')

from pathlib import Path
path_dir = Path(__file__).parent.parent.resolve()
path_json = path_dir / "data.JSON"

#logging
logger = logging.getLogger("content")

formatter = logging.Formatter("[%(asctime)s] %(levelname)-8s:%(name)-12s: %(message)s",
                              "%d-%m-%Y %H:%M:%S")
formatter.converter = time.gmtime

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
        utils.set_debug_level(logger)
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