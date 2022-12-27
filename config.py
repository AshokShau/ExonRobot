import json
import os


def get_user_list(config, key):
    with open("{}/Exon/{}".format(os.getcwd(), config), "r") as json_file:
        return json.load(json_file)[key]


class Config(object):
    LOGGER = True

    API_ID = "13600724"
    API_HASH = "ee59fd28d0d065c6b7d105082c6a0ba0"
    TOKEN = ""
    OWNER_ID = 5938660179
    OWNER_USERNAME = "Abishnoi1M"
    SUPPORT_CHAT = "AbishnoiMF"
    EVENT_LOGS = -1001573019550
    MONGO_DB_URI = "mongodb+srv://EXONTEST:EXONTEST@cluster0.qakcaii.mongodb.net/?retryWrites=true&w=majority"
    DATABASE_URL = "postgres://iokudnsr:NrFikOMi3zStM4x2dMXcsaZjIP8dYvd0@babar.db.elephantsql.com/iokudnsr"
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

    LOAD = []
    NO_LOAD = []
    INFOPIC = True
    URL = None
    DRAGONS = get_user_list("elevated_users.json", "sudos")
    DEV_USERS = get_user_list("elevated_users.json", "devs")
    SPAMMERS = None
    CERT_PATH = None
    DEL_CMDS = True
    STRICT_GBAN = True
    BAN_STICKER = "CAADBQAD1gkAAjvoCVXK6sii-SVBrAI"
    KICK_STICKER = "CAADBQADXAkAAlTD8VWDZUADwfd2CQI"
    ALLOW_EXCL = True
    BL_CHATS = []
    ALLOW_CHATS = True
    TEMP_DOWNLOAD_LOC = "./Downloads"


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
