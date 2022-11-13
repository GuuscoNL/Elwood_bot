import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import json
import logging

load_dotenv() # load all the variables from the env file
SERVER_ID = os.getenv('SERVER_ID')
ADMIN_ROLE_ID = int(os.getenv('ADMIN_ROLE_ID'))

from pathlib import Path
path_dir = Path(__file__).parent.parent.resolve()
path_json = path_dir / "data.JSON"

#logging
logger = logging.getLogger("restart")

formatter = logging.Formatter("[%(asctime)s] %(levelname)-8s:%(name)-12s: %(message)s",
                              "%Y-%m-%d %H:%M:%S")

file_handler = logging.FileHandler("main.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

class restart(commands.Cog):

    def __init__(self, bot : commands.Bot) -> None:
        self.bot  = bot
    
    @app_commands.command(
        name = "restart",
        description = "Restarts the bot")
    
    @app_commands.checks.has_any_role(ADMIN_ROLE_ID)
    async def restart(self, interaction : discord.Interaction) -> None:
        await set_debug_level()
        # Only restarts if in cloud, otherwise it just quits
        await interaction.response.send_message("Restarting...")
        logger.info(f"{interaction.user.name} restarted the bot")
        quit(0)
    
    @restart.error
    async def permission(self, interaction : discord.Interaction, error : app_commands.AppCommandError) -> None:
        
        if isinstance(error, app_commands.MissingAnyRole):
            await set_debug_level()
            if interaction.user.id == 397046303378505729:
                await interaction.response.send_message("Restarting...")
                logger.info(f"{interaction.user.name} restarted the bot")
                quit(0)
            else:
                await interaction.response.send_message("You do not have the permission!", ephemeral=True)
                logger.info(f"{interaction.user.name} tried to use the `/restart` command")

async def setup(bot : commands.Bot) -> None:
    await bot.add_cog(
        restart(bot),
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