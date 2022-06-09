import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import json

load_dotenv() # load the variables needed from the .env file
SERVER_ID =os.getenv('SERVER_ID')
ADMIN_ROLE_ID =os.getenv('ADMIN_ROLE_ID')

from pathlib import Path
path_dir = Path(__file__).parent.parent.resolve()
path_json = path_dir / "data.JSON"

class toggle_server(commands.Cog):

   def __init__(self, bot : commands.Bot) -> None:
      self.bot  = bot
      self.last_toggle = False
   
   @app_commands.command(
      name = "toggle_server",
      description = "toggles the send_server_info variable")

   @app_commands.checks.has_any_role(ADMIN_ROLE_ID) # Check if the author has the admin role. If not go to @json.error
   async def toggle_server(self, interaction : discord.Interaction) -> None:
      await self.update_json()
      await interaction.response.send_message(f"The send_server_info variable is set to {self.last_toggle}", ephemeral=True)
      
   @toggle_server.error
   async def permission(self, interaction : discord.Interaction, error : app_commands.AppCommandError) -> None:
      if isinstance(error, app_commands.MissingAnyRole): # Check if the error is because of an missing role
         if interaction.user.id == 397046303378505729:# Check if the author is me (GuuscoNL)
               await self.update_json()
               await interaction.response.send_message(f"The send_server_info variable is set to {self.last_toggle}", ephemeral=True)
         else:
               await interaction.response.send_message("You do not have the permission!", ephemeral=True)
   
   async def update_json(self):
      with path_json.open(mode="r+") as file:
         json_data = json.loads(file.read())
         self.last_toggle = not json_data["send_server_info"]
         json_data["send_server_info"] = self.last_toggle
         file.seek(0)
         temp = json.dumps(json_data, indent=3)
         file.truncate(0)
         file.write(temp)

async def setup(bot : commands.Bot) -> None:
   await bot.add_cog(
      toggle_server(bot),
      guilds = [discord.Object(id = SERVER_ID)]
   )