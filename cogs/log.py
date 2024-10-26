import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import time
import json
import logging
import utils

load_dotenv() # load all the variables from the env file
SERVER_ID = os.getenv('SERVER_ID')
ADMIN_ROLE_ID = int(os.getenv('ADMIN_ROLE_ID'))

from pathlib import Path
path_dir = Path(__file__).parent.parent.resolve()
path_json = path_dir / "data.JSON"

#logging
logger = logging.getLogger("log")

formatter = logging.Formatter("[%(asctime)s] %(levelname)-8s:%(name)-12s: %(message)s",
                              "%d-%m-%Y %H:%M:%S")
formatter.converter = time.gmtime

file_handler = logging.FileHandler("main.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

class log(commands.Cog):

    def __init__(self, bot : commands.Bot) -> None:
        self.bot  = bot
    
    @app_commands.command(
        name = "log",
        description = "Show the bots logs")

    @app_commands.checks.has_any_role(ADMIN_ROLE_ID) # Check if the author has the admin role. If not go to @log.error
    async def log(self, interaction : discord.Interaction) -> None:
        utils.set_debug_level(logger)
        await interaction.response.send_message("", file=discord.File("main.log"), ephemeral=True)
        logger.info(f"{interaction.user.name} used the `/log` command")
        
    @log.error
    async def permission(self, interaction : discord.Interaction, error : app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.MissingAnyRole): # Check if the error is because of an missing role
            utils.set_debug_level(logger)
            if interaction.user.id == 397046303378505729:# Check if the author is me (GuuscoNL)
                await interaction.response.send_message("", file=discord.File("main.log"), ephemeral=True)
                logger.info(f"{interaction.user.name} used the `/log` command")
            else:
                await interaction.response.send_message("You do not have permission to use this command!", ephemeral=True)
                logger.warning(f"{interaction.user.name} tried to use `/log`")

async def setup(bot : commands.Bot) -> None:
    await bot.add_cog(
        log(bot),
        guilds = [discord.Object(id = SERVER_ID)]
    )