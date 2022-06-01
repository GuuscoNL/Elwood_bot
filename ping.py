import discord
from discord import app_commands
from discord.ext import commands
#from main import SERVER_ID

SERVER_ID = 543042771070484491
ADMIN_ROLE_ID = 701895569060135005

class ping(commands.Cog):

    def __init__(self, bot : commands.Bot) -> None:
        self.bot  = bot
    
    @app_commands.command(
        name = "ping",
        description = "Pings the bot")

    @app_commands.checks.has_any_role(ADMIN_ROLE_ID)
    async def ping(self, interaction : discord.Interaction) -> None:
        await interaction.response.send_message(f"pong ({str(self.bot.latency*1000)[0:6]} ms)")
        
    @ping.error
    async def permission(self, interaction : discord.Interaction, error : app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.MissingAnyRole):
            if interaction.user.id == 397046303378505729:
                await interaction.response.send_message(f"pong ({str(self.bot.latency*1000)[0:6]} ms)")
            else:
                await interaction.response.send_message("You do not have the permission!", ephemeral=True)

async def setup(bot : commands.Bot) -> None:
    await bot.add_cog(
        ping(bot),
        guilds = [discord.Object(id = SERVER_ID)]
    )