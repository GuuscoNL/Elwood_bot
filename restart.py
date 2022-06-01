import discord
from discord import app_commands
from discord.ext import commands

SERVER_ID = 543042771070484491
ADMIN_ROLE_ID = 701895569060135005

class restart(commands.Cog):

    def __init__(self, bot : commands.Bot) -> None:
        self.bot  = bot
    
    @app_commands.command(
        name = "restart",
        description = "Restarts the bot")
    
    @app_commands.checks.has_any_role(ADMIN_ROLE_ID)
    async def restart(self, interaction : discord.Interaction) -> None:
        # Only restarts if in cloud, otherwise it just quits
        await interaction.response.send_message("Restarting...")
        quit(0)
    
    @restart.error
    async def permission(self, interaction : discord.Interaction, error : app_commands.AppCommandError) -> None:
        
        if isinstance(error, app_commands.MissingAnyRole):
            if interaction.user.id == 397046303378505729:
                await interaction.response.send_message("Restarting...")
                quit(0)
            else:
                await interaction.response.send_message("You do not have the permission!", ephemeral=True)

async def setup(bot : commands.Bot) -> None:
    await bot.add_cog(
        restart(bot),
        guilds = [discord.Object(id = SERVER_ID)]
    )