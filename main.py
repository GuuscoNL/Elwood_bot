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
    json_data["send_server_info"] = True
    json_data["debug"] = False
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
        await self.load_extension("cogs.debug")
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
            debug = json_data["debug"]
            self.send_server_info = json_data["send_server_info"]
            try:
                self.msg = await channel.fetch_message(msg_ID)
            except discord.NotFound:
                self.msg = None
        if self.send_server_info == True:
            message = await self.TBN() # Get the embed with the server info
            if self.msg == None: # if message doesn't exist create a new one
                print(f"[{await self.current_time()}] Starting server info")
                try:
                    self.msg = await channel.send(content=message)
                except discord.errors.HTTPException as e:
                    self.msg = await channel.send(content=f"ERROR too many players online, discord can't handle it (Must be 2000 or fewer characters.)\nMax players possible across both servers: 54\nMight get fixed in the future, I hope\n<@397046303378505729>\nLast update: <t:{int(time.time())}:R>")
                    print(e)
                except Exception as e:
                    self.msg = await channel.send(content=f"ERROR: {e}\n<@397046303378505729>")
                    print(e)
                await self.update_json_message_ID()
                    
            else:
                if debug: print(f"[{await self.current_time()}] Updated server information")
                try:
                    await self.msg.edit(content=message)
                except discord.errors.HTTPException as e:
                    self.msg = await self.msg.edit(content=f"ERROR too many players online, discord can't handle it (Must be 2000 or fewer characters.)\nMax players possible across both servers: 54\nMight get fixed in the future, I hope\n<@397046303378505729>\nLast update: <t:{int(time.time())}:R>")
                    print(e)
                except Exception as e:
                    self.msg = await self.msg.edit(content=f"ERROR: {e}\n<@397046303378505729>")
                    print(e)
    
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
            # ------ Get tables and get server infos ------ 
            main_address = ("46.4.12.78", 27015)
            event_address = ("46.4.12.78", 27016) 
            main_table = await self.Get_table(main_address)
            event_table = await self.Get_table(event_address)
            info_server_main = a2s.info(main_address)
            info_server_event = a2s.info(event_address)
            """
            #  ------ Make the embed ------ 
            em = discord.Embed(title="Server information", 
                            description="", #f"Players online: {info_server_main.player_count}/{info_server_main.max_players}\n```{main_table}```Last update <t:{int(time.time())}:R>", 
                            url="https://www.gametracker.com/server_info/46.4.12.78:27015/"
                            )
            em.add_field(name="Main server:", value=f"Players online: {info_server_main.player_count}/{info_server_main.max_players}\n```{main_table}```", inline=False)
            em.add_field(name="Event server:", value=f"Players online: {info_server_event.player_count}/{info_server_event.max_players}\n```{event_table}```", inline=False)
            em.add_field(name="Last update:", value=f"<t:{int(time.time())}:R>", inline=False)
            """
            message = "**Connect to server:** steam://connect/46.4.12.78:27015\n\n"
            message += "**Main server:**\n"
            message += f"Players online: {info_server_event.player_count}/{info_server_event.max_players}\n"
            message += f"```{main_table}```"
            message += f"```{event_table}```\n"
            message += "Last update: \n"
            message += f"<t:{int(time.time())}:R>"
            return message
        except Exception as e: # An error has occurred. Print it and put it in the embed
            if str(e) == "timed out":
                em = discord.Embed(title="Timed out",description=f"Probably a map restart or server is offline")
                em.set_footer(text="Ping Guus if this is still happening after 5 mins")
            else:
                print(f"--------------------------\n[{await self.current_time()}]\nERROR:\n{e}\n--------------------------\n")
                em = discord.Embed(title="An error occurred",description=f"{e}\nFIX THIS <@397046303378505729>",)
            return em
        
    async def Get_table(self, address):
        # ------ Get players online from server ------ 
        players_server = a2s.players(address)
        # ------ Make a list so that table2ascii can read it ------ 
        """ debug stuff. To test max players
        players = []
        for i in range(27):
            players.append(["GuuscoNL_"+ str(i),"00:00:00"])
        
        output = table2ascii(
                            header=["Player", "Time Played"],
                            body=players
                                )
        """
        players = []
        for i in range(len(players_server)):
            time_played = str(datetime.timedelta(seconds=int(players_server[0+i].duration))) # Convert seconds to h:m:s
            time_played = time_played[0:4] # only show hours and minutes
            player_name = players_server[0+i].name
            max_char = 17
            if len(player_name) > max_char:
                player_name = player_name[0:max_char-3]+"..."
            if player_name == "": # If player_name == "" than they are still connecting
                player_name = "Connecting..."
            temp = [player_name, time_played]
            players.append(temp)

        #  ------ Make the table ------ 
        output = table2ascii(
                            header=["Player", "Time Played"],
                            body=players
                                )
        return output

bot = Elwood()
bot.run(TOKEN) # run the bot with the token


