import asyncio
import logging
import os
import platform
import random
import sys
import time

import telegram.ext as tg
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient as MongoCli
from pymongo import MongoClient
from pyrogram import Client
from telegram import __bot_api_version__
from telegram import __version__ as ptb_version
from telegram.error import BadRequest, Forbidden
from telegram.ext import Application
from telethon import TelegramClient, events
from telethon.sessions import MemorySession

try:
    from config import *
except:
    print("ᴄᴀɴ'ᴛ ɪᴍᴘᴏʀᴛ ᴄᴏɴғɪɢ!")

load_dotenv()


StartTime = time.time()
# ᴇɴᴀʙʟᴇ ʟᴏɢɢɪɴɢ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

LOGGER = logging.getLogger(__name__)

# ɪғ ᴠᴇʀsɪᴏɴ < 3.9, sᴛᴏᴘ ʙᴏᴛ .
if sys.version_info[0] < 3 or sys.version_info[1] < 9:
    LOGGER.error(
        "ʏᴏᴜ MUST ʜᴀᴠᴇ ᴀ ᴘʏᴛʜᴏɴ ᴠᴇʀsɪᴏɴ ᴏғ ᴀᴛ ʟᴇᴀsᴛ 3.9! ᴍᴜʟᴛɪᴘʟᴇ ғᴇᴀᴛᴜʀᴇs ᴅᴇᴘᴇɴᴅ ᴏɴ ᴛʜɪs. ʙᴏᴛ ǫᴜɪᴛᴛɪɴɢ.",
    )
    quit(1)


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
CERT_PATH = Config.CERT_PATH
LOAD = Config.LOAD
NO_LOAD = Config.NO_LOAD
DEL_CMDS = Config.DEL_CMDS
STRICT_GBAN = Config.STRICT_GBAN
BAN_STICKER = Config.BAN_STICKER
KICK_STICKER = Config.KICK_STICKER
ALLOW_EXCL = Config.ALLOW_EXCL
INFOPIC = Config.INFOPIC
TEMP_DOWNLOAD_LOC = Config.TEMP_DOWNLOAD_LOC

DEV_USERS.add(OWNER_ID)
DRAGONS = list(DRAGONS) + list(DEV_USERS)
DEV_USERS = list(DEV_USERS)


telethn = TelegramClient(MemorySession(), API_ID, API_HASH)

app = Client("ExonRobot", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN)
app.start()

asu = app.get_me()
BOT_USERNAME = asu.username
BOT_NAME = asu.first_name
BOT_ID = asu.id

EXON_PTB = Application.builder().token(TOKEN).build()
asyncio.get_event_loop().run_until_complete(EXON_PTB.bot.initialize())

# ᴍᴏɴɢᴏ ᴅᴀᴛᴀʙᴀsᴇ
mongo = MongoCli(MONGO_DB_URI)
db = mongo.EXON

try:
    client = MongoClient(MONGO_DB_URI)
except PyMongoError:
    exiter(1)
mdb = client["EXONROBOT"]


# ᴇᴠᴇɴᴛs
def register(**args):
    """ʀᴇɢɪsᴛᴇʀs ᴀ ɴᴇᴡ ᴍᴇssᴀɢᴇ."""
    pattern = args.get("pattern")

    r_pattern = r"^[/!]"

    if pattern is not None and not pattern.startswith("(?i)"):
        args["pattern"] = "(?i)" + pattern

    args["pattern"] = pattern.replace("^/", r_pattern, 1)

    def decorator(func):
        telethn.add_event_handler(func, events.NewMessage(**args))
        return func

    return decorator


def Asuinline(**args):
    def decorator(func):
        telethn.add_event_handler(func, events.CallbackQuery(**args))
        return func

    return decorator


application = EXON_PTB
from Exon.modules.helper_funcs.handlers import (
    CustomCommandHandler,
    CustomMessageHandler,
)

tg.CommandHandler = CustomCommandHandler
tg.MessageHandler = CustomMessageHandler
