import json
import os
from os import getenv

from dotenv import load_dotenv

load_dotenv()


def get_user_list(config, key):
    with open("{}/Exon/{}".format(os.getcwd(), config), "r") as json_file:
        return json.load(json_file)[key]


class Config(object):
    LOGGER = True

    API_ID = int(getenv("API_ID"))
    API_HASH = getenv("API_HASH")
    TOKEN = getenv("TOKEN", None)  # ɢᴇᴛ ᴏɴᴇ ғʀᴏᴍ @BotFather [ᴅᴏɴ'ᴛ ᴀᴅᴅ ʜᴇᴀʀ ʙᴏᴛ ᴛᴏᴋᴇɴ ]
    OWNER_ID = int(getenv("OWNER_ID", "5938660179"))  # sᴛᴀʀᴛ @Exon_Robot ᴛʏᴘᴇ /id
    OWNER_USERNAME = getenv("OWNER_USERNAME", None)  # ʏᴏᴜʀᴇ ᴛɢ ᴜsᴇʀɴᴀᴍᴇ ᴡɪᴛʜᴏᴜᴛ @
    SUPPORT_CHAT = getenv(
        "SUPPORT_CHAT", "AbishnoiMF"
    )  # sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ ᴡɪᴛʜᴏᴜᴛ @
    EVENT_LOGS = int(
        getenv("EVENT_LOGS", "-1001573019550")
    )  # ʏᴏᴜʀ ʟᴏɢ ɢʀᴏᴜᴘ ɪᴅ ᴡɪᴛɢ (-)
    MONGO_DB_URI = getenv(
        "MONGO_DB_URI", ""
    )  # ʀᴇǫᴜɪʀᴇᴅ ғᴏʀ ᴅᴀᴛᴀʙᴀsᴇ ᴄᴏɴɴᴇᴄᴛɪᴏɴs (ᴍᴏɴɢᴏ - https://cloud.mongodb.com/)
    DB_NAME = getenv("DB_NAME", "EXON_2")  # ᴅʙ  ɴᴀᴍᴇ
    DATABASE_URL = getenv(
        "DATABASE_URL", ""
    )  # ʀᴇǫᴜɪʀᴇᴅ ғᴏʀ ᴅᴀᴛᴀʙᴀsᴇ ᴄᴏɴɴᴇᴄᴛɪᴏɴs (sǫʟ :- elephantsql.com).",

    # ɴᴏ ᴇᴅɪᴛ ᴢᴏɴᴇ
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

    LOAD = []
    NO_LOAD = []
    BL_CHATS = []
    DRAGONS = get_user_list("elevated_users.json", "sudos")  # ᴅᴏɴ'ᴛ ᴇᴅɪᴛ
    DEV_USERS = get_user_list("elevated_users.json", "devs")  # ᴅᴏɴ'ᴛ ᴇᴅɪᴛ


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
