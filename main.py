import discord
import a2s
import datetime
import os
import aiohttp
import time
import json
import logging
import asyncio
import socket
from discord.ext import commands, tasks
from dotenv import load_dotenv
from table2ascii import table2ascii
from aiohttp import ClientConnectorError
import pathlib


# ------ Constants that must be changed in .env for every server the bot is in ------ 
load_dotenv(override=True) # load all the variables from the env file
TOKEN =os.getenv('TOKEN')
SERVER_ID = int(os.getenv('SERVER_ID'))
CHANNEL_ID_SERVER_INFO = int(os.getenv('CHANNEL_ID_SERVER_INFO'))
ADMIN_ROLE_ID = int(os.getenv('ADMIN_ROLE_ID'))
UPDATE_DELAY = 60*5 # seconds


# ------ Initialise some stuff ------ 
from pathlib import Path
path_dir = Path(__file__).parent.resolve()
path_json = path_dir / "data.JSON"

# logging
logger = logging.getLogger("main")

formatter = logging.Formatter("[%(asctime)s] %(levelname)-8s:%(name)-12s: %(message)s",
                              "%d-%m-%Y %H:%M:%S")
formatter.converter = time.gmtime

file_handler = logging.FileHandler("main.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

# Discord.py logging
discord_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='a')


class Elwood(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents = discord.Intents.all(),
            application_id = 979113489387884554)
        self.msg = None
        self.channel = None
        self.main_server_info = None

    async def setup_hook(self): 
        self.session = aiohttp.ClientSession()
        
        # use apthlib
        cog_files = [file.stem for file in pathlib.Path("cogs").rglob("*.py")]
        
        for cog in cog_files:
            await self.load_extension(f"cogs.{cog}")

        await bot.tree.sync(guild = discord.Object(id = SERVER_ID))
        self.background.start()
    
    async def on_ready(self):
        with path_json.open() as file:
            data = json.loads(file.read())
            last_online_time = datetime.datetime.fromtimestamp(data["last_online"])

        time_difference = datetime.datetime.now() - last_online_time
        str_time_difference = str(time_difference).split(".")[0]
        logger.critical("")
        logger.critical(f"Last online: {last_online_time.strftime('%d-%m-%Y %H:%M:%S')}")
        logger.critical(f"Total time offline: {str_time_difference}")

        logger.info(f"{self.user} has connected to Discord!")
        print(f"{self.user} has connected to Discord!")


    @tasks.loop(seconds=UPDATE_DELAY)
    async def background(self) -> None:
        
        if not await self.prepare_background_task():
            # Unable to get server info
            return
        

        try:
            if "Maintenance" in self.main_server_info.server_name: # Is the server in Maintenance mode?
                await self.edit_message(await self.maintenance_mode_message())
            else:
                message, total_player_count = await self.TBN() # Get the message with the server info
                await self.edit_message(message)
                await self.channel.edit(name=f"🎮┃Active crew: {total_player_count}")

        except discord.HTTPException as e:
            await self.check_rate_limit(e)

    async def prepare_background_task(self) -> None:
        
        # ------ Get server info ------
        try:
            main_address = ("46.4.12.78", 27015) 
            self.main_server_info = a2s.info(main_address)
        except (TimeoutError, socket.timeout):
            return False
        except Exception as e:
            logger.error(f"Unable to get server info")
            logger.exception("  Unknown exception", e)
        
        # Get the channel where the message is
        if self.channel is None:
            self.channel = self.get_channel(CHANNEL_ID_SERVER_INFO)

        # Log when the bot was last online
        await self.update_json_last_online()

        # ----- Open json file and read it -----
        with path_json.open() as file:
            json_data = json.loads(file.read())
            msg_ID = json_data["message_ID"]
            await self.set_debug_level(json_data["loglevel"])
            
            # Update the message ID if it doesn't exist
            try:
                if self.msg is None:
                    self.msg = await self.channel.fetch_message(msg_ID)
            except discord.NotFound:
                self.msg = None
        
        return True
                
    async def check_maintenance_mode(self) -> bool:
        
            if "Maintenance" in self.main_server_info.server_name:
                return True
            return False
        
    
    @background.before_loop
    async def before_background(self) -> None:
        await self.wait_until_ready()
        logger.debug(f"Server info ready")

    async def check_permission(self, user_perms, needed_perm_id) -> bool: # Check if the user has a specific role
        for i in range(len(user_perms)):
            if user_perms[i].id == needed_perm_id:
                return True
        return False

    async def update_json_message_ID(self) -> None:
        with path_json.open(mode="r+") as file:
            json_data = json.loads(file.read())
            json_data["message_ID"] = self.msg.id
            file.seek(0)
            temp = json.dumps(json_data, indent=3)
            file.truncate(0)
            file.write(temp)

    async def update_json_last_online(self) -> None:
        with path_json.open(mode="r+") as file:
            json_data = json.loads(file.read())
            json_data["last_online"] = time.time()
            file.seek(0)
            temp = json.dumps(json_data, indent=3)
            file.truncate(0)
            file.write(temp)

    async def edit_message(self, message: str) -> None:
        if self.msg == None: # if message doesn't exist create a new one
            logger.debug(f"Starting server info")
            try:
                self.msg = await self.channel.send(content=message)
            except discord.errors.HTTPException as e: # too many characters in the message or rate limit
                await self.check_too_many_players(e)
                await self.check_rate_limit(e)
                
            except ClientConnectorError:
                logger.warning(f"ClientConnectorError: Retrying after {UPDATE_DELAY} seconds")
                
                await asyncio.sleep(UPDATE_DELAY)
                self.background.restart()
                
            except Exception as e:
                self.msg = await self.channel.send(content=f"ERROR: {e}")
                logger.exception("Unknown exception", e)
            await self.update_json_message_ID()

        else: # message exists
            logger.debug(f"Starting server info")
            try:
                await self.msg.edit(content=message)
            except discord.errors.HTTPException as e: # too many characters in the message or rate limit
                await self.check_too_many_players(e)
                await self.check_rate_limit(e)
            
            except ClientConnectorError:
                logger.warning(f"ClientConnectorError: Retrying after {UPDATE_DELAY} seconds")
                
                await asyncio.sleep(UPDATE_DELAY)
                self.background.restart()

            except Exception as e:
                self.msg = await self.msg.edit(content=f"ERROR: {e}")
                logger.exception("Unknown exception", e)

    async def check_rate_limit(self, e: discord.errors.HTTPException) -> None:
        if e.status == 429:
            total_retry_time = int(e.response.headers.get("Retry-After", 300))
            
            if total_retry_time > 3600:# an hour
                retry_after = 3600
            else:
                retry_after = total_retry_time

            logger.warning(f"RATE LIMITED: Retrying after {retry_after} seconds (Total retry time: {total_retry_time})")
            await asyncio.sleep(retry_after)
            
            self.background.restart()
    
    async def check_too_many_players(self, e: discord.errors.HTTPException) -> None:
        if e.status == 400 and e.code == 50035: # too many characters
            self.msg = await self.msg.edit(content=await self.too_many_players())
            logger.warning("Too many characters in the message")

    async def TBN(self) -> tuple[str, int]: # Get server info
        try:
            # ------ Get tables and get server infos ------ 
            main_info, player_count_main = await self.get_server_info(("46.4.12.78", 27015))
            event_info, player_count_event = await self.get_server_info(("46.4.12.78", 27016))
                
            message = "**Connect to server:** steam://connect/46.4.12.78:27015\n\n"
            message += "**Main server:**\n"
            message += main_info
            message += "**Event server:**\n"
            message += event_info
            message += "**Last update:** \n"
            message += f"<t:{int(time.time())}:R>"
            return message, player_count_main + player_count_event
        except Exception as e: # An error has occurred. Log it
            logger.exception(f"Exception in TBN()", e)
            message = f"**An error occurred**\n\n{e}\nFIX THIS <@397046303378505729>"
            return message, 0
    
    async def get_server_info(self, address: tuple[str, int]) -> tuple[str, int]:
        try:
            player_table = f"```{await self.get_table(address)}```\n"
            info_server = a2s.info(address)
            players_amount = f"Players online: {info_server.player_count}/{info_server.max_players}\n"
            return players_amount + player_table, info_server.player_count
        except TimeoutError:
            players_amount = ""
            player_table = "`Timed out`\nProbably a map restart or the server is offline\n"
            return players_amount + player_table, 0
        except Exception as e:
            players_amount = f"{e}\n"
            player_table = ""
            return players_amount + player_table, 0
    
    async def get_table(self, address: tuple[str, int]) -> str:
        # ------ Get players online from server ------ 
        players_server = a2s.players(address)
        
        # ------ Make a list so that table2ascii can read it ------ 
        players = []
        for player in players_server:
            hours = int(player.duration) // 3600
            minutes = (int(player.duration) % 3600) // 60

            time_played = f"{hours: 2}:{minutes:02}"
            player_name = player.name
            
            max_chars = 17
            if len(player_name) > max_chars:
                player_name = player_name[0:max_chars-3]+"..."

            if player_name == "": # If empty -> still connecting
                if address[1] == 27016:
                    player_name = "Transporting..."
                else:
                    player_name = "Connecting..."
            players.append((player_name, time_played))
        
        #  ------ Make the table ------ 
        output = table2ascii(
                            header=["Player", "Time Played"],
                            body=players
                                )
        return output
    
    async def set_debug_level(self, debuglevel):
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
    
    async def maintenance_mode_message(self) -> str:
        message = "**Connect to server:** steam://connect/46.4.12.78:27015\n\n"
        message += "The servers are currently in maintenance mode.\n\n"
        message += "**Last update:** \n"
        message += f"<t:{int(time.time())}:R>"
        return message
        
bot = Elwood()
bot.run(TOKEN, log_handler=discord_handler, log_level=logging.INFO) # run the bot with the token