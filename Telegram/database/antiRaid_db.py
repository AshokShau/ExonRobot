from typing import Dict, Optional, Union

from pymongo.errors import PyMongoError

from . import mongo
from .. import LOGGER


class AntiRaidDB:
    collection_name = "AntiRaid"

    def __init__(self, chat_id: int) -> None:
        self.collection = mongo.db[self.collection_name]
        self.chat_id = chat_id

    async def get_anti_raid(self) -> Dict[str, Optional[Union[str, bool]]]:
        # Default anti-raid settings if not found in the database
        default_settings = {
            "raid_mode": "ban",
            "ban_time": "30m",
            "raid_time": "15m",
            "anti_raid": False,
        }
        try:
            anti_raid = await self.collection.find_one({"_id": self.chat_id})
            return anti_raid or default_settings
        except PyMongoError as e:
            LOGGER.error(f"Error retrieving anti-raid for chat {self.chat_id}: {e}")
            return default_settings

    async def set_raid_mode(
        self, raid_mode: str
    ) -> Dict[str, Optional[Union[str, bool]]]:
        settings = await self.get_anti_raid()
        settings["raid_mode"] = raid_mode
        try:
            await self.collection.update_one(
                {"_id": self.chat_id}, {"$set": {"raid_mode": raid_mode}}, upsert=True
            )
            LOGGER.info(f"Raid mode for chat {self.chat_id} set to {raid_mode}.")
        except PyMongoError as e:
            LOGGER.error(f"Error setting raid mode for chat {self.chat_id}: {e}")
        return settings

    async def set_ban_time(
        self, ban_time: str
    ) -> Dict[str, Optional[Union[str, bool]]]:
        settings = await self.get_anti_raid()
        settings["ban_time"] = ban_time
        try:
            await self.collection.update_one(
                {"_id": self.chat_id}, {"$set": {"ban_time": ban_time}}, upsert=True
            )
            LOGGER.info(f"Ban time for chat {self.chat_id} set to {ban_time}.")
        except PyMongoError as e:
            LOGGER.error(f"Error setting ban time for chat {self.chat_id}: {e}")
        return settings

    async def set_raid_time(
        self, raid_time: str
    ) -> Dict[str, Optional[Union[str, bool]]]:
        settings = await self.get_anti_raid()
        settings["raid_time"] = raid_time
        try:
            await self.collection.update_one(
                {"_id": self.chat_id}, {"$set": {"raid_time": raid_time}}, upsert=True
            )
            LOGGER.info(f"Raid time for chat {self.chat_id} set to {raid_time}.")
        except PyMongoError as e:
            LOGGER.error(f"Error setting raid time for chat {self.chat_id}: {e}")
        return settings

    async def set_anti_raid(
        self, anti_raid: bool
    ) -> Dict[str, Optional[Union[str, bool]]]:
        settings = await self.get_anti_raid()
        settings["anti_raid"] = anti_raid
        try:
            await self.collection.update_one(
                {"_id": self.chat_id}, {"$set": {"anti_raid": anti_raid}}, upsert=True
            )
            LOGGER.info(f"Anti-raid for chat {self.chat_id} set to {anti_raid}.")
        except PyMongoError as e:
            LOGGER.error(f"Error setting anti-raid for chat {self.chat_id}: {e}")
        return settings
