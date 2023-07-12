import logging
import time

from aiohttp import ClientSession
from telegram.ext import Application, Defaults, PicklePersistence

from config import Config

StartTime = time.time()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)
logging.getLogger("apscheduler").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
LOGGER = logging.getLogger("[EXON]")

# ᴠᴇʀs
BOT_VERSION = "ᴠ3.0"
BAN_STICKER = "CAADBQAD1gkAAjvoCVXK6sii-SVBrAI"
KICK_STICKER = "CAADBQADXAkAAlTD8VWDZUADwfd2CQI"
TEMP_DOWNLOAD_LOC = "./downloads"
START_IMG = Config.START_IMG
TOKEN = Config.TOKEN
OWNER_ID = int(Config.OWNER_ID)
DRAGONS = set(int(x) for x in Config.DRAGONS or [])
DEV_USERS = set(int(x) for x in Config.DEV_USERS or [])
BL_CHATS = []
EVENT_LOGS = Config.EVENT_LOGS
SUPPORT_CHAT = Config.SUPPORT_CHAT
DB_URI = Config.DATABASE_URL
MONGO_DB_URL = Config.MONGO_DB_URL

DEV_USERS = list(DEV_USERS)
DRAGONS = list(DRAGONS) + list(DEV_USERS)


defaults = Defaults(disable_web_page_preview=True, block=False)
persistence = PicklePersistence(filepath="bot_data.pickle")

exon = (
    Application.builder()
    .token(TOKEN)
    .persistence(persistence)
    .defaults(defaults)
    .concurrent_updates(256)
    .connection_pool_size(512)
    .build()
)

aiohttpsession = ClientSession()
sw = None
BOT_ID = TOKEN.split(":")[0]

