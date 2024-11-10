import logging
import os
from time import time

import pytz
from ptbmod import TelegramHandler
from telegram import LinkPreviewOptions
from telegram.constants import ParseMode
from telegram.ext import Application, ApplicationBuilder, Defaults, PicklePersistence

import config
from Telegram.database import mongo

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs.txt"), logging.StreamHandler()],
    level=config.LOGGER_LEVEL,
)

logging.getLogger("apscheduler").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.ERROR)

LOGGER = logging.getLogger(__name__)

HELP_COMMANDS = {}
bot_data = "bot_data.pickle"

defaults = Defaults(
    allow_sending_without_reply=True,
    parse_mode=ParseMode.HTML,
    link_preview_options=LinkPreviewOptions(is_disabled=True),
    block=False,
    tzinfo=pytz.timezone(config.TIME_ZONE),
)


async def post_init(app: Application) -> None:
    """
    Initialize the application after startup.

    This function sets the bot's start time in the application data,
    which can be used to track how long the bot has been running.
    """
    await mongo.connect()
    app.bot_data["StartTime"] = time()


async def post_shutdown(_: Application) -> None:
    """Cleanup after shutdown.

    If the bot data file exists, remove it.
    """
    if os.path.exists(bot_data):
        os.remove(bot_data)
    await mongo.close()


application = (
    ApplicationBuilder()
    .token(config.TOKEN)
    .defaults(defaults)
    .read_timeout(80)
    .write_timeout(60)
    .get_updates_read_timeout(50)
    .post_init(post_init)
    .post_shutdown(post_shutdown)
    .concurrent_updates(True)
    .persistence(PicklePersistence(filepath=bot_data))
    .arbitrary_callback_data(True)
    .build()
)

Cmd = TelegramHandler(application).command
Msg = TelegramHandler(application).message
Cb = TelegramHandler(application).callback_query
Inline = TelegramHandler(application).inline_query
CMember = TelegramHandler(application).chat_member
