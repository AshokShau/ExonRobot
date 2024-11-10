from os import getenv

from dotenv import load_dotenv

load_dotenv()

TOKEN = getenv("TOKEN")
"bot token, get from @BotFather"

LOGGER_LEVEL = getenv("LOGGER_LEVEL")
"logger level, `debug(10)`, `info(20)`, `warn(30)` and `error(40)`. default is `info`"

MONGO = getenv("MONGO")
"mongo db uri, get from mongodb.com"

TIME_ZONE = getenv("TIME_ZONE", "Asia/Kolkata")
"bot time zone, get from https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"

OWNER_ID = int(getenv("OWNER_ID"))
"owner id, get from @GuardxRobot"

LOGGER_ID = int(getenv("LOGGER_ID"))
"logger id, get from @GuardxRobot"
