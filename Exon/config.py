"""
MIT License

Copyright (c) 2022 ABISHNOI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
# ""DEAR PRO PEOPLE,  DON'T REMOVE & CHANGE THIS LINE
# TG :- @Abishnoi
#     MY ALL BOTS :- Abishnoi_bots
#     GITHUB :- KingAbishnoi ""


import json
import os

from dotenv import load_dotenv

load_dotenv()


def get_user_list(config, key):
    with open("{}/Exon/{}".format(os.getcwd(), config), "r") as json_file:
        return json.load(json_file)[key]


class Config(object):
    LOGGER = True

    API_ID = "983922"
    API_HASH = ""
    EVENT_LOGS = "-1001497222182"
    DATABASE_URI = ""  # elephantsql.com
    MONGO_DB_URL = ""  # cloud.mongodb.com/
    TOKEN = ""
    OWNER_USERNAME = "Abishnoi1M"
    OWNER_ID = "1452219013"
    # ɴᴏᴛ ɪᴍᴘᴏʀᴛᴀɴᴛ ᴢᴏɴᴇ
    MONGO_DB = "Exon"  # Don't edit
    REDIS_URL = "redis://default:imP6xyfvlFsVpzFbciK3dIx9Vde05pav@redis-17127.c239.us-east-1-2.ec2.cloud.redislabs.com:17127/default"
    ARQ_API_URL = "https://arq.hamker.in"
    ARQ_API_KEY = "TENRCY-KDKSK-MSMSM-OXQYYO-ARQ"
    DONATION_LINK = "t.me/AbishnoiMF"
    HELP_IMG = "https://telegra.ph/file/14d1f98500af1132e5460.jpg"
    START_IMG = "https://telegra.ph/file/14d1f98500af1132e5460.jpg"
    UPDATES_CHANNEL = "Abishnoi_bots"
    SUPPORT_CHAT = "AbishnoiMF"
    INFOPIC = False
    GENIUS_API_TOKEN = "28jwoKAkskaSjsnsksAjnwjUJwj"
    SPAMWATCH_API = None
    REM_BG_API_KEY = None
    OPENWEATHERMAP_ID = None
    WALL_API = None
    TIME_API_KEY = None
    HEROKU_APP_NAME = None
    HEROKU_API_KEY = None
    NO_LOAD = ["rss", "cleaner", "connection", "math"]
    TEMP_DOWNLOAD_DIRECTORY = "./"
    LOAD = []
    DEL_CMDS = True
    BAN_STICKER = None
    WORKERS = 8
    STRICT_GBAN = True
    WEBHOOK = False
    URL = None
    PORT = []
    ALLOW_EXCL = []
    ALLOW_CHATS = True
    CERT_PATH = []
    SPAMWATCH_SUPPORT_CHAT = "AbishnoiMF"
    BOT_API_URL = "https://api.telegram.org/bot"
    DRAGONS = get_user_list("elevated_users.json", "sudos")  # don't edit
    DEV_USERS = get_user_list("elevated_users.json", "devs")  # ""
    REQUESTER = get_user_list("elevated_users.json", "whitelists")  # ""
    DEMONS = get_user_list("elevated_users.json", "supports")  # ""
    INSPECTOR = get_user_list("elevated_users.json", "sudos")  # ""
    TIGERS = get_user_list("elevated_users.json", "tigers")  # ""
    WOLVES = get_user_list("elevated_users.json", "whitelists")  # ""


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True


# ENJOY
