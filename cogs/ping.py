import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import utils

load_dotenv() # load all the variables from the env file
SERVER_ID = os.getenv('SERVER_ID')
ADMIN_ROLE_ID = int(os.getenv('ADMIN_ROLE_ID'))

class ping(commands.Cog):

    def __init__(self, bot : commands.Bot) -> None:
        self.bot  = bot
        self.logger = bot.cog_loggers[self.__class__.__name__]
    
    @app_commands.command(
        name = "ping",
        description = "Pings the bot")

    @app_commands.checks.has_any_role(ADMIN_ROLE_ID) # Check if the author has the admin role. If not go to @ping.error
    async def ping(self, interaction : discord.Interaction) -> None:
        utils.set_debug_level(self.logger)
        await interaction.response.send_message(f"pong ({str(self.bot.latency*1000)[0:6]} ms)", ephemeral=True)
        self.logger.info(f"{interaction.user.name} pinged the bot")
        
    @ping.error
    async def permission(self, interaction : discord.Interaction, error : app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.MissingAnyRole): # Check if the error is because of an missing role
            utils.set_debug_level(self.logger)
            if interaction.user.id == 397046303378505729:# Check if the author is me (GuuscoNL)
                await interaction.response.send_message(f"pong ({str(self.bot.latency*1000)[0:6]} ms)", ephemeral=True)
                self.logger.info(f"{interaction.user.name} pinged the bot")
            else:
                await interaction.response.send_message("You do not have permission to use this command!", ephemeral=True)
                self.logger.warning(f"{interaction.user.name} tried to use `/ping`")

async def setup(bot : commands.Bot) -> None:
    await bot.add_cog(
        ping(bot),
        guilds = [discord.Object(id = SERVER_ID)]
    )