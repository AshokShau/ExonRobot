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
    TOKEN = getenv("TOKEN", None)
    START_IMG = getenv(
        "START_IMG", "https://te.legra.ph/file/1298fa07d367674fba061.jpg"
    )
    OWNER_ID = int(getenv("OWNER_ID", "5938660179"))
    SUPPORT_CHAT = getenv("SUPPORT_CHAT", "AbishnoiMF")
    EVENT_LOGS = int(getenv("EVENT_LOGS", "-1001819078701"))
    MONGO_DB_URL = getenv("MONGO_DB_URL", None)
    DATABASE_URL = getenv("DATABASE_URL", None)
    DRAGONS = get_user_list("elevated_users.json", "sudos")
    DEV_USERS = get_user_list("elevated_users.json", "devs")


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
