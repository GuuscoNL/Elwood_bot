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
from a2s import SourceInfo
from dataclasses import dataclass
import pathlib as Path
from logging import Logger
from typing import Any

import utils

# ------ Constants that must be changed in .env for every server the bot is in ------ 
load_dotenv(override=True) # load all the variables from the env file
TOKEN =os.getenv('TOKEN')
SERVER_ID = int(os.getenv('SERVER_ID'))
CHANNEL_ID_SERVER_INFO = int(os.getenv('CHANNEL_ID_SERVER_INFO'))
ADMIN_ROLE_ID = int(os.getenv('ADMIN_ROLE_ID'))
UPDATE_DELAY = 60*5 # seconds

@dataclass
class ServerInfo:
    info: SourceInfo
    players: list[str]

class Elwood(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents = discord.Intents.all(),
            application_id = 979113489387884554)
        self.msg = None
        self.channel = None
        self.main_server_info:  ServerInfo = None
        self.event_server_info: ServerInfo = None


        # logging
        self.logger = self.create_logger("main")
        self.cog_loggers = {}
        
        # path to the json file
        path_dir = Path.Path(__file__).parent.resolve()
        self.path_json = path_dir / "data.JSON"
        

    async def setup_hook(self): 
        self.session = aiohttp.ClientSession()
        
        cog_files = [file.stem for file in Path.Path("cogs").rglob("*.py")]
        
        for cog in cog_files:
            self.cog_loggers[cog] = self.create_logger(cog)
            
            await self.load_extension(f"cogs.{cog}")

        await bot.tree.sync(guild = discord.Object(id = SERVER_ID))
        self.background.start()
    
    def create_logger(self, name: str) -> Logger:
        logger = logging.getLogger(name)

        formatter = logging.Formatter("[%(asctime)s] %(levelname)-8s:%(name)-12s: %(message)s",
                                    "%d-%m-%Y %H:%M:%S")
        formatter.converter = time.gmtime

        file_handler = logging.FileHandler("main.log")
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
        
        return logger
        
    
    async def on_ready(self):
        with self.path_json.open() as file:
            data = json.loads(file.read())
            last_online_time = datetime.datetime.fromtimestamp(data["last_online"])

        time_difference = datetime.datetime.now() - last_online_time
        str_time_difference = str(time_difference).split(".")[0]
        self.logger.critical("")
        self.logger.critical(f"Last online: {last_online_time.strftime('%d-%m-%Y %H:%M:%S')}")
        self.logger.critical(f"Total time offline: {str_time_difference}")

        self.logger.info(f"{self.user} has connected to Discord!")
        print(f"{self.user} has connected to Discord!")


    @tasks.loop(seconds=UPDATE_DELAY)
    async def background(self) -> None:
        
        await self.prepare_background_task()
        
        try:
            if "Maintenance" in self.main_server_info.info.server_name: # Is the server in Maintenance mode?
                await self.edit_message(await self.maintenance_mode_message())
            else:
                message, total_player_count = await self.get_servers_message() # Get the message with the server info
                await self.edit_message(message)
                await self.channel.edit(name=f"🎮┃Active crew: {total_player_count}")

        except discord.HTTPException as e:
            await self.check_rate_limit(e)

    async def prepare_background_task(self) -> None:
        
        # ------ Get server info ------
        try:
            main_address = ("46.4.12.78", 27015)
            self.main_server_info = await self.get_server_info(main_address)
        except (TimeoutError, socket.timeout):
            self.main_server_info = None
            return False
        except Exception as e:
            self.main_server_info = None
            self.logger.error("Unable to get server info")
            self.logger.exception("  Unknown exception", e)
        
        try:
            event_address = ("46.4.12.78", 27016)
            self.event_server_info = await self.get_server_info(event_address)
        except (TimeoutError, socket.timeout):
            self.event_server_info = None
            return False
        except Exception as e:
            self.event_server_info = None
            self.logger.error("Unable to get server info")
            self.logger.exception("  Unknown exception", e)

        # Get the channel where the message is
        if self.channel is None:
            self.channel = self.get_channel(CHANNEL_ID_SERVER_INFO)

        # Log when the bot was last online
        await self.update_json("last_online", time.time())

        # ----- Open json file and read it -----
        with self.path_json.open() as file:
            json_data = json.loads(file.read())
            msg_ID = json_data["message_ID"]
            
            # Update the message ID if it doesn't exist
            try:
                if self.msg is None:
                    self.msg = await self.channel.fetch_message(msg_ID)
            except discord.NotFound:
                self.msg = None
        
        # Set the debug level
        utils.set_debug_level(self.logger)
        
        return True

    async def get_server_info(self, address: tuple[str, int]) -> dict:
        try:
            return ServerInfo(a2s.info(address), a2s.players(address))
        except TimeoutError:
            self.logger.warning(f"Timed out while getting server info from {address}")
            return None
        except Exception as e:
            self.logger.error(f"Unable to get server info from {address}")
            self.logger.exception("  Unknown exception", e)
            return None

    
    @background.before_loop
    async def before_background(self) -> None:
        await self.wait_until_ready()
        self.logger.debug("Server info ready")

    async def update_json(self, key: str, value: Any) -> None:
        with self.path_json.open(mode="r+") as file:
            json_data = json.loads(file.read())
            json_data[key] = value
            file.seek(0)
            temp = json.dumps(json_data, indent=3)
            file.truncate(0)
            file.write(temp)

    async def edit_message(self, message: str) -> None:
        if self.msg is None: # if message doesn't exist create a new one
            self.logger.debug("Creating new server info message")
            try:
                self.msg = await self.channel.send(content=message)
            except discord.errors.HTTPException as e: # too many characters in the message or rate limit
                await self.check_too_many_players(e)
                await self.check_rate_limit(e)
                
            except ClientConnectorError:
                self.logger.warning(f"ClientConnectorError: Retrying after {UPDATE_DELAY} seconds")
                
                await asyncio.sleep(UPDATE_DELAY)
                self.background.restart()
                
            except Exception as e:
                self.logger.exception("Unknown exception when creating new server info message", e)
            await self.update_json("message_ID", self.msg.id)

        else: # message exists
            self.logger.debug("Reusing server info message")
            try:
                await self.msg.edit(content=message)
            except discord.errors.HTTPException as e: # too many characters in the message or rate limit
                await self.check_too_many_players(e)
                await self.check_rate_limit(e)
            
            except ClientConnectorError:
                self.logger.warning(f"ClientConnectorError: Retrying after {UPDATE_DELAY} seconds")
                
                await asyncio.sleep(UPDATE_DELAY)
                self.background.restart()

            except Exception as e:
                self.logger.exception("Unknown exception when trying to reuse server info message", e)

    async def check_rate_limit(self, e: discord.errors.HTTPException) -> None:
        if e.status == 429:
            total_retry_time = int(e.response.headers.get("Retry-After", 300))
            
            if total_retry_time > 3600:# an hour
                retry_after = 3600
            else:
                retry_after = total_retry_time

            self.logger.warning(f"RATE LIMITED: Retrying after {retry_after} seconds (Total retry time: {total_retry_time})")
            await asyncio.sleep(retry_after)
            
            self.background.restart()
    
    async def check_too_many_players(self, e: discord.errors.HTTPException) -> None:
        if e.status == 400 and e.code == 50035: # too many characters
            self.msg = await self.msg.edit(content=await self.too_many_players())
            self.logger.warning("Too many characters in the message")

    async def get_servers_message(self) -> tuple[str, int]:
        # ------ Get tables and get server infos ------ 
        if self.main_server_info is not None:
            main_info, player_count_main = await self.get_online_players(self.main_server_info)
        else:
            main_info, player_count_main = "`Timed out`\nProbably a map restart or the server is offline\n", 0
            
        if self.event_server_info is not None:
            event_info, player_count_event = await self.get_online_players(self.event_server_info)
        else:
            event_info, player_count_event = "`Timed out`\nProbably a map restart or the server is offline\n", 0
        
        message = "**Connect to server:** steam://connect/46.4.12.78:27015\n\n"
        message += "**Main server:**\n"
        message += main_info
        message += "**Event server:**\n"
        message += event_info
        message += "**Last update:** \n"
        message += f"<t:{int(time.time())}:R>"
        return message, player_count_main + player_count_event
    
    async def get_online_players(self, server_info: ServerInfo) -> tuple[str, int]:
        player_table = f"```{await self.get_table(server_info)}```\n"
        players_amount = f"Players online: {server_info.info.player_count}/{server_info.info.max_players}\n"
        return players_amount + player_table, server_info.info.player_count

    
    async def get_table(self, server_info: ServerInfo) -> str:
        
        players_server = server_info.players
        
        # ------ Make a list so that table2ascii can read it ------ 
        players = []
        for player in players_server:
            hours = int(player.duration) // 3600
            minutes = (int(player.duration) % 3600) // 60

            time_played = f"{hours: 2}:{minutes:02}"
            player_name = player.name
            
            max_chars = 17
            if len(player_name) > max_chars:
                player_name = player_name[0:max_chars - 3] + "..."

            if player_name == "": # If empty -> still connecting
                if server_info.info.port == 27016:
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

    async def too_many_players(self) -> str:
        players_main = f"Players online: {self.main_server_info.info.player_count}/{self.main_server_info.info.max_players}\n"
        players_event = f"Players online: {self.event_server_info.info.player_count}/{self.event_server_info.info.max_players}\n"
        
        ERROR_MESSAGE = "\n**Players not shown**\nToo many players online, discord can't handle it\n\n"
        
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

if __name__ == "__main__":
    # ------ Run the bot ------
    bot = Elwood()
    bot.run(TOKEN, log_handler=logging.FileHandler(filename='discord.log', encoding='utf-8', mode='a'), log_level=logging.INFO) # run the bot with the token