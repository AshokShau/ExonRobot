from typing import Union, Dict, List
from pymongo.errors import PyMongoError
from . import mongo
from .. import LOGGER


class WarnsDB:
    collection_name = "Warns"

    def __init__(self, chat_id: int) -> None:
        self.collection = mongo.db[self.collection_name]
        self.chat_id = chat_id

    async def get_warns(self, user_id: int) -> Dict[str, Union[List[str], int]]:
        # Default warning data if not found in the database
        default_data = {
            "warns": [],  # List to store warnings (e.g., reason for warning)
            "num_warns": 0,  # Count of warnings
            "warn_limit": 5,  # Maximum number of warnings before action
            "warn_mode": "none",  # The warning mode (e.g., "none", "kick", "ban")
        }
        try:
            warn_data = await self.collection.find_one({"_id": self.chat_id})
            return warn_data.get("warned_users", {}).get(user_id, default_data)
        except PyMongoError as e:
            LOGGER.error(
                f"Error retrieving warns for user {user_id} in chat {self.chat_id}: {e}"
            )
            return default_data

    async def warn_user(
        self, user_id: int, warn_reason: str = None
    ) -> Dict[str, Union[List[str], int]]:
        try:
            warn_data = await self.collection.find_one({"_id": self.chat_id}) or {
                "warned_users": {},
                "warn_limit": 5,
                "warn_mode": "none",
            }
            user_warnings = warn_data["warned_users"].get(user_id, [])
            user_warnings.append(warn_reason)
            warn_data["warned_users"][user_id] = user_warnings

            await self.collection.update_one(
                {"_id": self.chat_id},
                {"$set": {"warned_users": warn_data["warned_users"]}},
                upsert=True,
            )
            LOGGER.info(
                f"User {user_id} warned in chat {self.chat_id}. Total warns: {len(user_warnings)}"
            )
            return {"warns": user_warnings, "num_warns": len(user_warnings)}
        except PyMongoError as e:
            LOGGER.error(f"Error warning user {user_id} in chat {self.chat_id}: {e}")
            return {"warns": [], "num_warns": 0}

    async def remove_warn(self, user_id: int) -> Dict[str, Union[List[str], int]]:
        try:
            warn_data = await self.collection.find_one({"_id": self.chat_id}) or {
                "warned_users": {},
                "warn_limit": 5,
                "warn_mode": "none",
            }
            user_warnings = warn_data["warned_users"].get(user_id, [])
            if user_warnings:
                user_warnings.pop()
            warn_data["warned_users"][user_id] = user_warnings

            await self.collection.update_one(
                {"_id": self.chat_id},
                {"$set": {"warned_users": warn_data["warned_users"]}},
                upsert=True,
            )
            LOGGER.info(
                f"Warn removed for user {user_id} in chat {self.chat_id}. Total warns: {len(user_warnings)}"
            )
            return {"warns": user_warnings, "num_warns": len(user_warnings)}
        except PyMongoError as e:
            LOGGER.error(
                f"Error removing warn for user {user_id} in chat {self.chat_id}: {e}"
            )
            return {"warns": [], "num_warns": 0}

    async def reset_warns(self, user_id: int) -> bool:
        try:
            warn_data = await self.collection.find_one({"_id": self.chat_id}) or {
                "warned_users": {}
            }
            if user_id in warn_data["warned_users"]:
                del warn_data["warned_users"][user_id]
                await self.collection.update_one(
                    {"_id": self.chat_id},
                    {"$set": {"warned_users": warn_data["warned_users"]}},
                    upsert=True,
                )
                LOGGER.info(f"Warns reset for user {user_id} in chat {self.chat_id}.")
            return True
        except PyMongoError as e:
            LOGGER.error(
                f"Error resetting warns for user {user_id} in chat {self.chat_id}: {e}"
            )
            return False

    async def get_warn_settings(self) -> Dict[str, Union[str, int]]:
        # Default warning settings if not found
        default_settings = {"warn_mode": "none", "warn_limit": 5}
        try:
            warn_data = await self.collection.find_one({"_id": self.chat_id})
            return (
                {
                    "warn_mode": warn_data.get("warn_mode", "none"),
                    "warn_limit": warn_data.get("warn_limit", 5),
                }
                if warn_data
                else default_settings
            )
        except PyMongoError as e:
            LOGGER.error(f"Error retrieving warn settings for chat {self.chat_id}: {e}")
            return default_settings

    async def set_warn_settings(self, warn_mode: str, warn_limit: int) -> bool:
        try:
            await self.collection.update_one(
                {"_id": self.chat_id},
                {"$set": {"warn_mode": warn_mode, "warn_limit": warn_limit}},
                upsert=True,
            )
            LOGGER.info(
                f"Warn settings updated for chat {self.chat_id}: mode={warn_mode}, limit={warn_limit}"
            )
            return True
        except PyMongoError as e:
            LOGGER.error(f"Error setting warn settings for chat {self.chat_id}: {e}")
            return False
