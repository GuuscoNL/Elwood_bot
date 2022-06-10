import discord
import a2s
import datetime
import os
import aiohttp
import time
import json
from discord.ext import commands, tasks
from dotenv import load_dotenv
from table2ascii import table2ascii

#TODO: Find a way to store message ID after restart. using a JSON file only works 
# locally, because heroku does not save the JSON file between restarts.

# ------ Constants that must be changed in .env for every server the bot is in ------ 
load_dotenv() # load all the variables from the env file
TOKEN =os.getenv('TOKEN')
SERVER_ID = int(os.getenv('SERVER_ID'))
CHANNEL_ID_SERVER_INFO = int(os.getenv('CHANNEL_ID_SERVER_INFO'))
ADMIN_ROLE_ID = int(os.getenv('ADMIN_ROLE_ID'))
UPDATE_DELAY = 60 # seconds

from pathlib import Path
path_dir = Path(__file__).parent.resolve()
path_json = path_dir / "data.JSON"

with path_json.open(mode="r+") as file:
    json_data = {}
    json_data["message_ID"] = 0
    json_data["send_server_info"] = False
    file.seek(0)
    temp = json.dumps(json_data, indent=3)
    file.truncate(0)
    file.write(temp)

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
        await self.load_extension("cogs.toggle_server")
        await self.load_extension("cogs.guus")
        await self.load_extension("cogs.invite")
        await self.load_extension("cogs.json")
        await bot.tree.sync(guild = discord.Object(id = SERVER_ID))
        self.background.start()
    
    async def on_ready(self):
        print(f"[{await self.current_time()}] {self.user} has connected to Discord!")
        
    # async def on_message(self, message):
    #     # ------ Check that the message is not from the bot itself ------ 
    #     if message.author.id == self.user.id:
    #         return
        
    #     # ------ Does the author have the ADMIN role? ------ 
    #     if message.author.id == 397046303378505729: # Check if the author is me (GuuscoNL)
    #         is_admin = True
    #     else:
    #         is_admin = await self.check_permission(message.author.roles, ADMIN_ROLE_ID) # Check if the author has the admin role

    @tasks.loop(seconds=UPDATE_DELAY)
    async def background(self):
        channel = self.get_channel(CHANNEL_ID_SERVER_INFO) # Get the channel where the server info will be posted
        with path_json.open() as file:
            json_data = json.loads(file.read())
            msg_ID = json_data["message_ID"]
            self.send_server_info = json_data["send_server_info"]
            try:
                self.msg = await channel.fetch_message(msg_ID)
            except discord.NotFound:
                self.msg = None
        if self.send_server_info == True:
            em = await self.TBN() # Get the embed with the server info
            if self.msg == None: # if message doesn't exist create a new one
                print(f"[{await self.current_time()}] Starting server info")
                self.msg = await channel.send(embed=em, content="Connect to server: steam://connect/46.4.12.78:27015")
                await self.update_json_message_ID()
                    
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
    
    async def update_json_message_ID(self):
        with path_json.open(mode="r+") as file:
            json_data = json.loads(file.read())
            json_data["message_ID"] = self.msg.id
            file.seek(0)
            temp = json.dumps(json_data, indent=3)
            file.truncate(0)
            file.write(temp)
            
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
                player_name = players_server[0+i].name
                if player_name == "": # If player_name == "" than they are still connecting
                    player_name = "Connecting..."
                temp = [player_name, time_played]
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
bot.run(TOKEN) # run the bot with the token

    


