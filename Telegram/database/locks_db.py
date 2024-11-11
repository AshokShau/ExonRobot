from typing import Union

from pymongo.errors import PyMongoError

from . import mongo
from .. import LOGGER


class LockDB:
    collection_name = "Locks"

    def __init__(self, chat_id: int) -> None:
        self.collection = mongo.db[self.collection_name]
        self.chat_id = chat_id

    async def get_locks(self) -> dict[str, Union[list, bool]]:
        # Default lock settings if not found in the database
        default_settings = {"locked": [], "lock_warn": False}
        try:
            locks = await self.collection.find_one({"_id": self.chat_id})
            return locks or default_settings
        except PyMongoError as e:
            LOGGER.error(f"Error retrieving locks for chat {self.chat_id}: {e}")
            return default_settings

    async def add_lock(self, lock_type: Union[str, list[str]]) -> bool:
        try:
            current_locks = (await self.get_locks())["locked"]
            if isinstance(lock_type, str):
                lock_type = [lock_type]
            current_locks.extend(lock_type)
            new_locks = list(set(current_locks))
            await self.collection.update_one(
                {"_id": self.chat_id},
                {"$set": {"locked": new_locks}},
                upsert=True,
            )
            LOGGER.info(f"Lock(s) added for chat {self.chat_id}: {lock_type}")
            return True
        except PyMongoError as e:
            LOGGER.error(f"Error adding lock(s) for chat {self.chat_id}: {e}")
            return False

    async def is_locked(self, lock_type: str) -> bool:
        try:
            current_locks = (await self.get_locks())["locked"]
            return lock_type in current_locks
        except PyMongoError as e:
            LOGGER.error(f"Error checking lock status for chat {self.chat_id}: {e}")
            return False

    async def remove_lock(self, lock_type: Union[str, list[str]]) -> bool:
        try:
            current_locks = (await self.get_locks())["locked"]
            if isinstance(lock_type, str):
                lock_type = [lock_type]
            new_locks = [lock for lock in current_locks if lock not in lock_type]
            if len(new_locks) != len(current_locks):
                await self.collection.update_one(
                    {"_id": self.chat_id},
                    {"$set": {"locked": new_locks}},
                    upsert=True,
                )
                LOGGER.info(f"Lock(s) removed for chat {self.chat_id}: {lock_type}")
                return True
            return False
        except PyMongoError as e:
            LOGGER.error(f"Error removing lock(s) for chat {self.chat_id}: {e}")
            return False

    async def unlock_all(self) -> bool:
        try:
            await self.collection.update_one(
                {"_id": self.chat_id}, {"$set": {"locked": []}}, upsert=True
            )
            LOGGER.info(f"All locks removed for chat {self.chat_id}.")
            return True
        except PyMongoError as e:
            LOGGER.error(f"Error removing all locks for chat {self.chat_id}: {e}")
            return False

    async def set_lock_warn(self, lock_warn: bool) -> bool:
        try:
            await self.collection.update_one(
                {"_id": self.chat_id}, {"$set": {"lock_warn": lock_warn}}, upsert=True
            )
            LOGGER.info(f"Lock warn for chat {self.chat_id} set to {lock_warn}.")
            return True
        except PyMongoError as e:
            LOGGER.error(f"Error setting lock warn for chat {self.chat_id}: {e}")
            return False

    async def get_lock_warn(self) -> bool:
        try:
            return (await self.get_locks()).get("lock_warn", False)
        except PyMongoError as e:
            LOGGER.error(f"Error retrieving lock warn for chat {self.chat_id}: {e}")
            return False

    @classmethod
    async def get_all_locks(cls, limit: int = 100000) -> list[dict]:
        collection = mongo.db[cls.collection_name]
        try:
            locks = await collection.find().limit(limit).to_list(length=limit)
            LOGGER.info(f"Retrieved {len(locks)} locked chats.")
            return locks
        except PyMongoError as e:
            LOGGER.error(f"Error retrieving all locked chats: {e}")
            return []
