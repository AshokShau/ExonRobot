from typing import Optional

from pymongo.errors import PyMongoError

from . import mongo
from .. import LOGGER


class AfkDB:
    collection_name = "Afk"

    def __init__(self, user_id: int) -> None:
        self.collection = mongo.db[self.collection_name]
        self.user_id = user_id

    async def check_afk(self) -> Optional[dict]:
        try:
            return await self.collection.find_one({"_id": self.user_id})
        except PyMongoError as e:
            LOGGER.error(f"Error retrieving afk for user {self.user_id}: {e}")
            return None

    async def add_afk(self, time, reason, media_type, media=None) -> bool:
        try:
            await self.collection.update_one(
                {"_id": self.user_id},
                {
                    "$set": {
                        "reason": reason,
                        "time": time,
                        "media_type": media_type,
                        "media": media,
                    }
                },
                upsert=True,
            )
            LOGGER.info(f"Afk for user {self.user_id} added or updated successfully.")
            return True
        except PyMongoError as e:
            LOGGER.error(f"Error adding afk for user {self.user_id}: {e}")
            return False

    async def remove_afk(self) -> bool:
        try:
            result = await self.collection.delete_one({"_id": self.user_id})
            if result.deleted_count > 0:
                LOGGER.info(f"Afk for user {self.user_id} removed successfully.")
                return True
            LOGGER.warning(
                f"Afk for user {self.user_id} delete found no matching documents."
            )
            return False
        except PyMongoError as e:
            LOGGER.error(f"Error deleting afk for user {self.user_id}: {e}")
            return False

    async def get_all_afk(self, limit: int = 100000) -> list[dict]:
        try:
            afk_users = await self.collection.find().limit(limit).to_list(length=limit)
            LOGGER.info(f"Retrieved {len(afk_users)} afk users.")
            return afk_users
        except PyMongoError as e:
            LOGGER.error(f"Error retrieving all afk users: {e}")
            return []

    @classmethod
    async def get_afk(cls, user_id: int) -> Optional[dict]:
        collection = mongo.db[cls.collection_name]
        try:
            return await collection.find_one({"_id": user_id})
        except PyMongoError as e:
            LOGGER.error(f"Error retrieving afk for user {user_id}: {e}")
            return None
