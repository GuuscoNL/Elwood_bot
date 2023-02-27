import discord
from discord import app_commands
from discord.ext import commands
from discord import ui
from dotenv import load_dotenv
import os
import json
import logging

load_dotenv() # load all the variables from the env file
SERVER_ID = os.getenv('SERVER_ID')
ADMIN_ROLE_ID = int(os.getenv('ADMIN_ROLE_ID'))

from pathlib import Path
path_dir = Path(__file__).parent.parent.resolve()
path_rank_json = path_dir / "rank_data.JSON"
path_json = path_dir / "data.JSON"

JSON_DATA = None
permission_roles = []
with path_rank_json.open() as file:
    JSON_DATA = json.loads(file.read())
    for role_id, _ in JSON_DATA["promotion_perms"].items():
        permission_roles.append(int(role_id))
        

#logging
logger = logging.getLogger("rank")

formatter = logging.Formatter("[%(asctime)s] %(levelname)-8s:%(name)-12s: %(message)s",
                              "%Y-%m-%d %H:%M:%S")

file_handler = logging.FileHandler("main.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

class rank(commands.Cog):

    def __init__(self, bot : commands.Bot) -> None:
        self.bot  = bot
    
    @app_commands.command(
        name = "rank",
        description = "Change someones rank")

    @app_commands.checks.has_any_role(*permission_roles)
    async def rank(self, interaction : discord.Interaction) -> None:
        await set_debug_level()

        view = rankView(interaction=interaction)
        await view.update_selectRole()
        await interaction.response.send_message(view=view, ephemeral=True)
        view.message = await interaction.original_response()
        await view.wait()
            
    @rank.error
    async def permission(self, interaction : discord.Interaction, error : app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.MissingAnyRole): # Check if the error is because of an missing role
            await set_debug_level()
            if interaction.user.id == 397046303378505729:# Check if the author is me (GuuscoNL)
                await set_debug_level()

                view = rankView(interaction=interaction)
                await view.update_selectRole()
                await interaction.response.send_message(view=view, ephemeral=True)
                view.message = await interaction.original_response()
                await view.wait()
            else:
                await interaction.response.send_message("You do not have permission to use this command!", ephemeral=True)
                logger.warning(f"{interaction.user.name} tried to use `/rank`")

class rankView(ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__(timeout=180)
        self.user_selected: discord.Member = None
        self.role_id_selected: int = None
        self.mode = 0
        self.user = interaction.user
        self.original_interaction: discord.Interaction = interaction
        self.all_role_options: list = JSON_DATA["all_ranks"]
        self.blacklist: list = JSON_DATA["blacklist"]
        self.guild = interaction.guild
        self.rank_channel = self.guild.get_channel(JSON_DATA["rank_channel_id"])
        
        # Check what the permission role is
        self.permission_role = None
        promotion_perms_reversed = reversed(JSON_DATA["promotion_perms"])
        for perm in promotion_perms_reversed:
            
            if self.permission_role != None: break
            for role in self.user.roles:
                if int(perm) == role.id:
                    self.permission_role = role
                    break
        
        self.selectMode = SelectMode()
        self.selectMode.options = [discord.SelectOption(label="Add rank", value= 0, default=True),
                                discord.SelectOption(label="Remove rank", value= 1)]
        self.add_item(self.selectMode)

        self.selectUser = SelectUser()
        self.add_item(self.selectUser)
        
        self.selectRole = SelectRole()
        self.selectRole.options = [discord.SelectOption(label="None", value= 0)] # Needed to prevent crash
        # Fill the options
        self.add_item(self.selectRole)

    async def update_selectRole(self) -> bool:
        
        if self.user_selected == None: return False# no user selected
        
        allowed_ranks_to_change_ids = []

        for index, role_id in enumerate(self.all_role_options):
            
            if index > JSON_DATA["promotion_perms"][str(self.permission_role.id)]: break
            allowed_ranks_to_change_ids.append(role_id)
        
        if self.mode == 0: # Add rank
            self.selectRole.options.clear()
            
            for role_id in allowed_ranks_to_change_ids:
                role = self.original_interaction.guild.get_role(role_id)
                
                if not role in self.user_selected.roles: # Does the user not have the rank?
                    self.selectRole.options.append(discord.SelectOption(label=role.name, value=role_id))
                
        elif self.mode == 1: # remove rank
            self.selectRole.options.clear()
            for user_role in self.user_selected.roles:
                if user_role.id in allowed_ranks_to_change_ids: # Does the user have the rank?
                    self.selectRole.options.append(discord.SelectOption(label=user_role.name, value=user_role.id))
            
            if self.selectRole.options == []: # No ranks to remove?
                # Needed to prevent crash
                self.selectRole.options.append(discord.SelectOption(label="No ranks that you can remove", value= 0))
                
        else:
            logger.error("Unknown mode in `/rank`")
            await self.original_interaction.response.send_message(f"An error ocurred:\n`Unknown mode`", ephemeral=True)
            await self.disable_all_items()
            self.stop()
            
        await self.message.edit(view=self)
    
    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)
    
    @ui.button(label="Confirm", row=4, style=discord.ButtonStyle.success)
    async def confirm_callback(self, interaction: discord.Interaction, button: ui.Button):
        
        # Check if a user is selected
        if self.user_selected == None:
            await interaction.response.send_message(f"You forgot to select a user", ephemeral=True)
            return
        
        # Check if user is in the blacklist
        if self.user_selected.id in self.blacklist:
            await interaction.response.send_message(f"You can't change {self.user_selected.mention}'s rank", ephemeral=True)
            return
        
        # Can't add or remove your own rank
        if self.user.id == self.user_selected.id:
            await interaction.response.send_message(f"You can't add or remove a rank to yourself", ephemeral=True)
            return
        
        # Can't add or remove a bots rank
        if self.user_selected.bot:
            await interaction.response.send_message(f"You can't add or remove a rank to a bot", ephemeral=True)
            return
        
        # Check if a role is selected
        if self.role_id_selected == None or self.role_id_selected == 0:
            if self.mode == 1:
                await interaction.response.send_message(f"No ranks that you can remove", ephemeral=True)
            else:
                await interaction.response.send_message(f"You forgot to select a role", ephemeral=True)
            await interaction.response.defer()
            return
        
        role = self.original_interaction.guild.get_role(int(self.role_id_selected))
        
        if self.mode == 0: # add role
            await self.user_selected.add_roles(role, reason=f"{self.user.name} added the rank `{role.name}` to {self.user_selected.name} via `/rank`")
            await interaction.response.send_message(f"The rank {role.mention} has been added to {self.user_selected.mention}", ephemeral=True)

            em = discord.Embed(title=f"Rank Added",
                               description=f"The rank {role.mention} has been added to {self.user_selected.mention}",
                               colour=discord.Colour.green())
            em.set_author(name=self.user.name, icon_url=self.user.display_avatar.url)
            
            await self.rank_channel.send(embed=em)
            logger.info(f"{self.user.name} added the rank `{role.name}` to {self.user_selected.name}")
        
        elif self.mode == 1: # remove role
            await self.user_selected.remove_roles(role, reason=f"{self.user.name} removed the rank `{role.name}` from {self.user_selected.name} via `/rank`")
            await interaction.response.send_message(f"The rank {role.mention} has been removed from {self.user_selected.mention}", ephemeral=True)
            
            em = discord.Embed(title=f"Rank Removed",
                               description=f"The rank {role.mention} has been removed from {self.user_selected.mention}",
                               colour=discord.Colour.red())
            em.set_author(name=self.user.name, icon_url=self.user.display_avatar.url)
            
            await self.rank_channel.send(embed=em)
            
            logger.info(f"{self.user.name} removed the rank `{role.name}` from {self.user_selected.name}")
        await self.disable_all_items()
        
    
    @ui.button(label="Cancel", row=4, style=discord.ButtonStyle.danger)
    async def cancel_callback(self, interaction: discord.Interaction, button: ui.Button):
        await self.disable_all_items()
        await interaction.response.defer()
    
    async def UserSelect_callback(self, interaction: discord.Interaction, choices):
        self.user_selected = choices[0]
        await self.update_selectRole()
        await interaction.response.defer()
        
    async def RoleSelect_callback(self, interaction: discord.Interaction, choices):
        self.role_id_selected = int(choices[0])
        await interaction.response.defer()
    
    async def ModeSelect_callback(self,interaction: discord.Interaction, choices):
        self.mode = int(choices[0])

        await self.update_selectRole()
        for option in self.selectMode.options:
            if int(option.value) == int(choices[0]):
                option.default = True
            else:
                option.default = False
        
        await self.message.edit(view=self)
        await interaction.response.defer()
    
    async def on_timeout(self) -> None:
        await self.disable_all_items()
        self.stop()

class SelectMode(ui.Select):
    def __init__(self):
        super().__init__(placeholder='Select a mode', min_values=1, max_values=1, row=1)
    
    async def callback(self, interaction: discord.Interaction):
        await self.view.ModeSelect_callback(interaction, self.values)

class SelectUser(ui.UserSelect):
    def __init__(self):
        super().__init__(placeholder='Select a user', min_values=1, max_values=1, row=2)
    
    async def callback(self, interaction: discord.Interaction):
        await self.view.UserSelect_callback(interaction, self.values)
        
class SelectRole(ui.Select):
    def __init__(self):
        super().__init__(placeholder='Select a role', min_values=1, max_values=1, row=3)
    
    async def callback(self, interaction: discord.Interaction):
        await self.view.RoleSelect_callback(interaction, self.values)

async def setup(bot : commands.Bot) -> None:
    await bot.add_cog(
        rank(bot),
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
        
        
""" Main server
Officers can promote this ranks - 1053531693404913757 ([Officer])
1064478722507423825 - Crewman 1st
1064478718644457482 - Crewman 2nd
934471618527391774 - Crewman 3rd

Senior Staff can promote this ranks - 1049816500413943859 ([Senior Staff])
934471617176801330 - Lieutenant 
934535840321916988 - Lieutenant Junior Grade
934471617352982550 - Ensign
1053525344373706882 - Warrant Officer
1064477540468666378 - Senior Chief Petty Officer
955945030302957598 - Chief Petty Officer
1064477431332872264 - Petty Officer 1st
1064477531618672680 - Petty Officer 2nd
955944401992040468 - Petty Officer 3rd

XO and CO can promote this ranks - 964150568752934953 (Executive Officer)
934471615603965952 - Lieutenant Commander
1064478033303572520 - Master Chief Petty Officer

CO can promote this ranks - 1039557590356602952 (Commanding Officer)
934473363278155848 - Commander
1064478122977808425 - Command Master Chief Petty Officer    
"""

""" dev server
Officers can promote this ranks - 1074123829493907487 ([Officer])
1074763301872992336 - Crewman 1st
1074763274224152737 - Crewman 2nd
1074123271139766272 - Crewman 3rd

Senior Staff can promote this ranks - 1074123309844807731 ([Senior Staff])
1074763568240656445- Lieutenant 
1074763541820756038- Lieutenant Junior Grade
1074763511168770068- Ensign
1074763460119908444 - Warrant Officer
1074763437185454160 - Senior Chief Petty Officer
1074763417228955788- Chief Petty Officer
1074763375785033829 - Petty Officer 1st
1074763354767380560 - Petty Officer 2nd
1074763332973768834- Petty Officer 3rd

XO and CO can promote this ranks - 1074792863650549770 (Executive Officer)
1074763593867853914- Lieutenant Commander
1074763488729256027 - Master Chief Petty Officer

CO can promote this ranks - 1074793250734481488 (Commanding Officer)
1074763618102554645- Commander
1074763650121871450 - Command Master Chief Petty Officer    
"""