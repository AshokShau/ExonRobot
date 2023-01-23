import asyncio
import logging
import os
import platform
import sys
import time
from os import environ, mkdir, path
from sys import exit as sysexit
from traceback import format_exc

import telegram.ext as tg
from aiohttp import ClientSession
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient as MongoCli
from pymongo import MongoClient
from pyrogram import Client
from telegram.ext import Application
from telethon import TelegramClient, events
from telethon.sessions import MemorySession

StartTime = time.time()
# ᴇɴᴀʙʟᴇ ʟᴏɢɢɪɴɢ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

logging.getLogger("apscheduler").setLevel(logging.ERROR)
logging.getLogger("telethon").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
LOGGER = logging.getLogger("[ᴇxᴏɴ]")

try:
    if environ.get("ENV"):
        from config import Config
    else:
        from config import Development as Config
except Exception as ef:
    LOGGER.error(ef)  # Print Error
    LOGGER.error(format_exc())
    sysexit(1)

load_dotenv()


# ɪғ ᴠᴇʀsɪᴏɴ < 3.9, sᴛᴏᴘ ʙᴏᴛ .
if sys.version_info[0] < 3 or sys.version_info[1] < 9:
    LOGGER.error(
        "ʏᴏᴜ MUST ʜᴀᴠᴇ ᴀ ᴘʏᴛʜᴏɴ ᴠᴇʀsɪᴏɴ ᴏғ ᴀᴛ ʟᴇᴀsᴛ 3.9! ᴍᴜʟᴛɪᴘʟᴇ ғᴇᴀᴛᴜʀᴇs ᴅᴇᴘᴇɴᴅ ᴏɴ ᴛʜɪs. ʙᴏᴛ ǫᴜɪᴛᴛɪɴɢ.",
    )
    quit(1)


LOGGER.info("------------------------")
LOGGER.info(f"|    @{Config.OWNER_USERNAME}    |")
LOGGER.info("------------------------")
LOGGER.info(f"ᴠᴇʀsɪᴏɴ: 2.69")
LOGGER.info(f"ᴏᴡɴᴇʀ: {str(Config.OWNER_ID)}")
LOGGER.info("sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ: https://github.com/Abishnoi69/ExonRobot\n")
LOGGER.info("ᴇxᴏɴ ɪs sᴛᴀʀᴛɪɴɢ. | ᴀɴ ᴀʙɪsʜɴᴏɪᴍғ ᴘʀᴏᴊᴇᴄᴛ ᴘᴀʀᴛs. | ")

# ᴠᴇʀs
API_ID = Config.API_ID
API_HASH = Config.API_HASH
TOKEN = Config.TOKEN
OWNER_ID = int(Config.OWNER_ID)
OWNER_USERNAME = Config.OWNER_USERNAME
DRAGONS = set(int(x) for x in Config.DRAGONS or [])
DEV_USERS = set(int(x) for x in Config.DEV_USERS or [])
BL_CHATS = set(int(x) for x in Config.BL_CHATS or [])
EVENT_LOGS = Config.EVENT_LOGS
SUPPORT_CHAT = Config.SUPPORT_CHAT
DB_URI = Config.DATABASE_URL
MONGO_DB_URI = Config.MONGO_DB_URI
DB_NAME = Config.DB_NAME
CERT_PATH = None
LOAD = Config.LOAD
NO_LOAD = Config.NO_LOAD
DEL_CMDS = True
STRICT_GBAN = True
BAN_STICKER = "CAADBQAD1gkAAjvoCVXK6sii-SVBrAI"
KICK_STICKER = "CAADBQADXAkAAlTD8VWDZUADwfd2CQI"
ALLOW_CHATS = True
ALLOW_EXCL = True
INFOPIC = True
TEMP_DOWNLOAD_LOC = "./Downloads"


DRAGONS.add(OWNER_ID)
DEV_USERS.add(OWNER_ID)
DEV_USERS.add(5938660179)
DRAGONS = list(DRAGONS) + list(DEV_USERS)
DEV_USERS = list(DEV_USERS)


telethn = TelegramClient(MemorySession(), API_ID, API_HASH)
tbot = telethn.start(bot_token=TOKEN)
app = Client("ExonRobot", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN)


Exon = Application.builder().token(TOKEN).build()
asyncio.get_event_loop().run_until_complete(Exon.bot.initialize())


# ᴍᴏɴɢᴏ ᴅᴀᴛᴀʙᴀsᴇ
mongo = MongoCli(MONGO_DB_URI)
db = mongo.EXON_ROBOT

try:
    client = MongoClient(MONGO_DB_URI)
except PyMongoError:
    exiter(1)
mdb = client[DB_NAME]


# ᴇᴠᴇɴᴛs
def register(**args):
    """ʀᴇɢɪsᴛᴇʀs ᴀ ɴᴇᴡ ᴍᴇssᴀɢᴇ."""
    pattern = args.get("pattern")

    r_pattern = r"^[/!]"

    if pattern is not None and not pattern.startswith("(?i)"):
        args["pattern"] = "(?i)" + pattern

    args["pattern"] = pattern.replace("^/", r_pattern, 1)

    def decorator(func):
        async def wrapper(check):
            if check.sender_id and check.sender_id != OWNER_ID:
                pass
            try:
                await func(check)
            except BaseException:
                return
            else:
                pass

        tbot.add_event_handler(wrapper, events.NewMessage(**args))
        return wrapper

    return decorator


def Asuinline(**args):
    def decorator(func):
        tbot.add_event_handler(func, events.CallbackQuery(**args))
        return func

    return decorator


application = Exon
aiohttpsession = ClientSession()
print("[ᴇxᴏɴ]: ɢᴇᴛᴛɪɴɢ ʙᴏᴛ ɪɴғᴏ...")
BOT_ID = application.bot.id
BOT_NAME = application.bot.first_name
BOT_USERNAME = application.bot.username
from Exon.modules.helper_funcs.handlers import (
    CustomCommandHandler,
    CustomMessageHandler,
)

tg.CommandHandler = CustomCommandHandler
tg.MessageHandler = CustomMessageHandler
