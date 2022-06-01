import discord
import a2s
import datetime
import os
import aiohttp
import time
from discord.ext import commands, tasks
from dotenv import load_dotenv
from table2ascii import table2ascii

load_dotenv() # load all the variables from the env file

# ------ Constants that must be changed for every server the bot is in ------ 
SERVER_ID = 543042771070484491
CHANNEL_ID_SERVER_INFO = 980213685198946324
ADMIN_ROLE_ID = 701895569060135005
UPDATE_DELAY = 60 # seconds

#TODO: Find a way to share variables between cogs file and this file (DOESN'T WORK FOR SOME DAMN REASON)
#      temp solution is to use ! commands on_message() instead of / commands in cogs.

class Elwood(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents = discord.Intents.all(),
            application_id = 979113489387884554)
        self.send_server_info = False
        self.msg = None


    async def setup_hook(self): 
        self.session = aiohttp.ClientSession()
        await self.load_extension("cogs.restart")
        await self.load_extension("cogs.ping")
        await self.load_extension("cogs.content")
        await self.load_extension("cogs.help")
        await self.load_extension("cogs.roll")
        await self.load_extension("cogs.guus")
        await self.load_extension("cogs.invite")
        await bot.tree.sync(guild = discord.Object(id = SERVER_ID))
        self.background.start()
    
    async def on_ready(self):
        print(f"[{await self.current_time()}] {self.user} has connected to Discord!")
        print("IT WORKED")
        
    async def on_message(self, message):
        # ------ Check that the message is not from the bot itself ------ 
        if message.author.id == self.user.id:
            return
        
        # ------ Does the author have the ADMIN role? ------ 
        if message.author.id == 397046303378505729:
            is_admin = True
        else:
            is_admin = await self.check_permission(message.author.roles, ADMIN_ROLE_ID)
        
        if message.content.startswith("!send_server_info"):
            # ------ If admin do it, else say no perms ------
            if is_admin:
                await message.reply(f"send_server_info = {self.send_server_info}")
            else:
                await message.reply(f"You do not have permission") # Tell the author that they do not have permission
                print(f"[{await self.current_time()}] {message.author.name} tried to use the `!send_server_info` command") # Log it
            
        if message.content.startswith("!toggle_server"):
            # ------ If admin do it, else say no perms ------ 
            if is_admin:
                self.send_server_info = not self.send_server_info # toggle send_server_info
                print(f"[{await self.current_time()}] {message.author.name} changed send_server_info to {self.send_server_info}") # log it
                if self.send_server_info == False and self.msg != None:
                    em = await self.TBN()
                    em.set_footer(text="Not updating")
                    await self.msg.edit(embed=em, content="Connect to server: steam://connect/46.4.12.78:27015") # If False say 'not updating' in server info message
                    await message.reply(f"The send_server_info variable is set to {self.send_server_info}")
                else: 
                    await message.reply(f"The send_server_info variable is set to {self.send_server_info} (Will update within {UPDATE_DELAY} seconds)")
            else:
                await message.reply(f"You do not have permission") # Tell the author that they do not have permission
                print(f"[{await self.current_time()}] {message.author.name} tried to use the `!toggle_server` command") # Log it

    @tasks.loop(seconds=UPDATE_DELAY)
    async def background(self):
        if self.send_server_info == True:
            channel = self.get_channel(CHANNEL_ID_SERVER_INFO) # Get the channel where the server info will be posted
            em = await self.TBN() # Get the embed with the server info
            if self.msg == None: # if message doesn't exist create a new one
                print(f"[{await self.current_time()}] Starting server info")
                self.msg = await channel.send(embed=em, content="Connect to server: steam://connect/46.4.12.78:27015")
            else:
                print(f"[{await self.current_time()}] Updated server information")
                await self.msg.edit(embed=em, content="Connect to server: steam://connect/46.4.12.78:27015")
        
    
    @background.before_loop
    async def before_background(self):
        await self.wait_until_ready()
        print(f"[{await self.current_time()}] Server info ready")

    async def check_permission(self, user_perms, needed_perm_id): # Check if the user has a specific role
        for i in range(len(user_perms)):
            if user_perms[i].id == needed_perm_id:
                return True
        return False
    
    async def current_time(self): # Get current time
        now = datetime.datetime.utcnow()
        return now.strftime("%d/%m/%Y %H:%M:%S UTC")

    async def TBN(self): # Put server info in embed
        try:
            # ------ Connect to the server and get info ------ 
            address = ("46.4.12.78", 27015)
            players_server = a2s.players(address)
            info_server = a2s.info(address)

            # ------ Make a list so that table2ascii can read it ------ 
            players = []
            for i in range(len(players_server)):
                time_played = str(datetime.timedelta(seconds=int(players_server[0+i].duration))) # Convert seconds to h:m:s
                temp = [players_server[0+i].name, time_played]
                players.append(temp)

            #  ------ Make the table ------ 
            output = table2ascii(
                                header=["Player", "Time Played"],
                                body=players
                                )
            
            #  ------ Make the embed ------ 
            em = discord.Embed(title="Server information", 
                            description=f"Players online: {info_server.player_count}/{info_server.max_players}\n```{output}```Last update <t:{int(time.time())}:R>", 
                            url="https://www.gametracker.com/server_info/46.4.12.78:27015/"
                            )
            return em
        except Exception as e: # An error has occurred. Print it and put it in the embed
            print(f"--------------------------\n[{await self.current_time()}]\nERROR:\n{e}\n--------------------------\n")
            em = discord.Embed(title="An error occurred",description=e)
            return em

bot = Elwood()
TOKEN =os.getenv('TOKEN')
bot.run(TOKEN) # run the bot with the token

    


