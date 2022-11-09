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

# MODES:
#   0 = sleep_mode
#   1 = Normal
#   2 = Holiday

# with path_json.open(mode="r+") as file:
#     json_data = {}
#     json_data["message_ID"] = 987496250091913236
#     json_data["mode"] = 2
#     json_data["debug"] = False
#     file.seek(0)
#     temp = json.dumps(json_data, indent=3)
#     file.truncate(0)
#     file.write(temp)

class Elwood(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents = discord.Intents.all(),
            application_id = 979113489387884554)
        self.msg = None
        self.sleep_unix_time = None
        self.new_time_sleep = True
        self.new_time_holi = True

    async def setup_hook(self): 
        self.session = aiohttp.ClientSession()
        await self.load_extension("cogs.restart")
        await self.load_extension("cogs.ping")
        await self.load_extension("cogs.content")
        await self.load_extension("cogs.help")
        await self.load_extension("cogs.roll")
        await self.load_extension("cogs.holiday_mode")
        await self.load_extension("cogs.guus")
        await self.load_extension("cogs.invite")
        await self.load_extension("cogs.json")
        await self.load_extension("cogs.debug")
        await self.load_extension("cogs.stardate")
        await self.load_extension("cogs.sleep_mode")
        await self.load_extension("cogs.talk")
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
    async def background(self) -> None:
        channel = self.get_channel(CHANNEL_ID_SERVER_INFO) # Get the channel where the server info will be posted
        
        # ----- Open json file and read it -----
        with path_json.open() as file:
            json_data = json.loads(file.read())
            msg_ID = json_data["message_ID"]
            debug = json_data["debug"]
            mode = json_data["mode"]
            try:
                self.msg = await channel.fetch_message(msg_ID)
            except discord.NotFound:
                self.msg = None

        if mode == 1: # Should the bot display the players
            self.new_time_sleep = True
            self.new_time_holi = True
            serverInMaintenance = False
            try:
                main_address = ("46.4.12.78", 27015) 
                info_server_event = a2s.info(main_address)
                if "Maintenance" in info_server_event.server_name: serverInMaintenance = True
            except TimeoutError: # Let TBN() handle the error
                pass
            except:
                print(f"[{await self.current_time()}] Unable to get server info to check if it is in maintenance mode")
                return
            
            if serverInMaintenance: # Is the server in Maintenance mode?
                if self.msg == None:
                    print(f"[{await self.current_time()}] Starting server info")
                    
                    try:
                        self.msg = await channel.send(content=await self.maintenance_mode_message(), suppress=True)
                    except discord.errors.HTTPException as e: # too many characters in the message
                        self.msg = await channel.send(content=await self.too_many_players())
                        print(e)
                    except Exception as e:
                        self.msg = await channel.send(content=f"ERROR: {e}\n<@397046303378505729>")
                        print(e)
                    await self.update_json_message_ID()
                
                else: # display the players
                    if debug: print(f"[{await self.current_time()}] Updated server information")
                    try:
                        await self.msg.edit(content=await self.maintenance_mode_message(), suppress=True)
                    except discord.errors.HTTPException as e: # too many characters in the message
                        self.msg = await self.msg.edit(content=await self.too_many_players())
                        print(e)
                    except Exception as e:
                        self.msg = await self.msg.edit(content=f"ERROR: {e}\n<@397046303378505729>")
                        print(e)
                return
            
            message = await self.TBN() # Get the message with the server info
            if self.msg == None: # if message doesn't exist create a new one
                print(f"[{await self.current_time()}] Starting server info")
                try:
                    self.msg = await channel.send(content=message)
                except discord.errors.HTTPException as e: # too many characters in the message
                    self.msg = await channel.send(content=await self.too_many_players())
                    print(e)
                except Exception as e:
                    self.msg = await channel.send(content=f"ERROR: {e}\n<@397046303378505729>")
                    print(e)
                await self.update_json_message_ID()
                    
            else: # message exists
                if debug: print(f"[{await self.current_time()}] Updated server information")
                try:
                    await self.msg.edit(content=message)
                except discord.errors.HTTPException as e: # too many characters in the message
                    self.msg = await self.msg.edit(content=await self.too_many_players())
                    print(e)
                except Exception as e:
                    self.msg = await self.msg.edit(content=f"ERROR: {e}\n<@397046303378505729>")
                    print(e)
        
        elif mode == 0: # Sleep_mode
            self.new_time_holi = True
            if self.msg == None: # if message doesn't exist create a new one
                print(f"[{await self.current_time()}] Starting server info")
                try:
                    self.msg = await channel.send(content="...")
                except discord.errors.HTTPException as e: # too many characters in the message
                    self.msg = await channel.send(content=await self.too_many_players())
                    print(e)
                except Exception as e:
                    self.msg = await channel.send(content=f"ERROR: {e}\n<@397046303378505729>")
                    print(e)
                await self.update_json_message_ID()
            
            try:
                if self.new_time_sleep: self.sleep_unix_time = time.time()
                await self.msg.edit(content=await self.sleep_mode_message(self.sleep_unix_time))
                self.new_time_sleep = False
                    
            except Exception as e:
                self.msg = await self.msg.edit(content=f"ERROR: {e}\n<@397046303378505729>")
                print(e)
        
        elif mode == 2: # Holiday_mode
            self.new_time_sleep = True
            if self.msg == None: # if message doesn't exist create a new one
                print(f"[{await self.current_time()}] Starting server info")
                try:
                    self.msg = await channel.send(content="...")
                except discord.errors.HTTPException as e: # too many characters in the message
                    self.msg = await channel.send(content=await self.too_many_players())
                    print(e)
                except Exception as e:
                    self.msg = await channel.send(content=f"ERROR: {e}\n<@397046303378505729>")
                    print(e)
                await self.update_json_message_ID()
            try:
                if self.new_time_holi: self.sleep_unix_time = time.time()
                await self.msg.edit(content=await self.holiday_mode_message(self.sleep_unix_time), suppress=True)
                self.new_time_holi = False
                    
            except Exception as e:
                self.msg = await self.msg.edit(content=f"ERROR: {e}\n<@397046303378505729>")
                print(e)
            
    
    @background.before_loop
    async def before_background(self) -> None:
        await self.wait_until_ready()
        print(f"[{await self.current_time()}] Server info ready")

    async def check_permission(self, user_perms, needed_perm_id) -> bool: # Check if the user has a specific role
        for i in range(len(user_perms)):
            if user_perms[i].id == needed_perm_id:
                return True
        return False
    
    async def current_time(self) -> None: # Get current time
        now = datetime.datetime.utcnow()
        return now.strftime("%d/%m/%Y %H:%M:%S UTC")
    
    async def update_json_message_ID(self) -> None:
        with path_json.open(mode="r+") as file:
            json_data = json.loads(file.read())
            json_data["message_ID"] = self.msg.id
            file.seek(0)
            temp = json.dumps(json_data, indent=3)
            file.truncate(0)
            file.write(temp)
            
    async def TBN(self) -> str: # Get server info
        try:
            # ------ Get tables and get server infos ------ 
            try:
                main_address = ("46.4.12.78", 27015)
                main_table = f"```{await self.Get_table(main_address)}```\n"
                info_server_main = a2s.info(main_address)
                players_main = f"Players online: {info_server_main.player_count}/{info_server_main.max_players}\n"
            except TimeoutError:
                players_main = ""
                main_table = "`Timed out`\nProbably a map restart or the server is offline\n\nPing Guus if this is still happening after 5 minutes *while* the server is online.\n\n"
            except Exception as e:
                players_main = f"{type(e)}\n"
                main_table = ""
            
            try:
                event_address = ("46.4.12.78", 27016) 
                event_table = f"```{await self.Get_table(event_address)}```\n"
                info_server_event = a2s.info(event_address)
                players_event = f"Players online: {info_server_event.player_count}/{info_server_event.max_players}\n"
                
            except TimeoutError:
                players_event = ""
                event_table = "`Timed out`\nProbably a map restart or the server is offline\n\nPing Guus if this is still happening after 5 minutes *while* the server is online.\n\n"
                
            except Exception as e:
                players_event = f"{type(e)}\n"
                event_table = ""
                
            message = "**Connect to server:** steam://connect/46.4.12.78:27015\n\n"
            message += "**Main server:**\n"
            message += players_main
            message += main_table
            message += "**Event server:**\n"
            message += players_event
            message += event_table
            message += "**Last update:** \n"
            message += f"<t:{int(time.time())}:R>"
            return message
        except Exception as e: # An error has occurred. Print it and put it in the message
            print(f"-----------------------------------\n[{await self.current_time()}] ERROR:\n{e}\n-----------------------------------\n")
            message = f"**An error occurred**\n\n{e}\nFIX THIS <@397046303378505729>"
            return message
        
    async def Get_table(self, address) -> str:
        # ------ Get players online from server ------ 
        players_server = a2s.players(address)
        # ------ Make a list so that table2ascii can read it ------ 
        """ #debug stuff. To test max players
        players = []
        for i in range(21):
            players.append(["GuuscoNL_"+ str(i) + (6*"0"),"00:00:00"])
        
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
                if address[1] == 27016:
                    player_name = "Transporting..."
                else:
                    player_name = "Connecting..."
            temp = [player_name, time_played]
            players.append(temp)
        
        #  ------ Make the table ------ 
        output = table2ascii(
                            header=["Player", "Time Played"],
                            body=players
                                )
        return output

    async def too_many_players(self) -> str:
        main_address = ("46.4.12.78", 27015)
        info_server_main = a2s.info(main_address)
        players_main = f"Players online: {info_server_main.player_count}/{info_server_main.max_players}\n"
        event_address = ("46.4.12.78", 27016) 
        info_server_event = a2s.info(event_address)
        players_event = f"Players online: {info_server_event.player_count}/{info_server_event.max_players}\n"
        
        ERROR_MESSAGE = f"\n**Players not shown**\nToo many players online, discord can't handle it\n\n"
        
        message = "**Connect to server:** steam://connect/46.4.12.78:27015\n\n"
        message += "**Main server:**\n"
        message += players_main
        message += "\n**Event server:**\n"
        message += players_event
        message += ERROR_MESSAGE
        message += "**Last update:** \n"
        message += f"<t:{int(time.time())}:R>"
        return message
    
    async def sleep_mode_message(self, unix_time) -> str:
        message = "**Connect to server:** steam://connect/46.4.12.78:27015\n\n"
        message += "I am sleeping, please do not disturb me. I will not respond to anything."
        message += "\n\n**Last awake:** \n"
        message += f"<t:{int(unix_time)}:R>"
        return message
    
    async def holiday_mode_message(self, unix_time) -> str:
        message = "**Connect to server:** Server is on a hiatus\n\n"
        message += "I am going back to Chicago to visit my brother Jake. \nIt's only 106 miles to Chicago, I got a full tank of gas, half a pack of cigarettes, it's dark... and I am wearing sunglasses.\n**HIT IT!**"
        message += "\nTo calculate the stardate you can use this link: https://shorturl.at/BGRUZ"
        message += "\n\n**Back from holiday:** \n"
        message += f"<t:1667779200:R>"
        return message
    
    async def maintenance_mode_message(self) -> str:
        message = "**Connect to server:** steam://connect/46.4.12.78:27015\n\n"
        message += "The server is currently in maintenance mode."
        return message
        
bot = Elwood()
bot.run(TOKEN) # run the bot with the token


