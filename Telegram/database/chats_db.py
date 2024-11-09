from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import PyMongoError

from . import mongo
from .. import LOGGER

class Chats:
    collection_name = "chats"

    def __init__(self, chat_id: int, collection: Optional[AsyncIOMotorCollection] = None) -> None:
        """
        Initialize the Chats class with a specific MongoDB collection.
        """
        self.collection = collection or mongo.db[self.collection_name]
        self.chat_id = chat_id

    async def get_chat(self) -> Optional[dict]:
        """Retrieve a single chat document by its ID."""
        try:
            chat = await self.collection.find_one({"_id": self.chat_id})
            return chat
        except Exception as e:
            LOGGER.error(f"Error retrieving chat with ID {self.chat_id}: {e}")
            return None

    async def update_chat(self, title: str, username: str) -> bool:
        """Update the title of a specific chat, or insert if it doesn't exist."""
        try:
            result = await self.collection.update_one(
                {"_id": self.chat_id},
                {"$set": {"title": title, "username": username}},
                upsert=True
            )
            if result.matched_count > 0:
                LOGGER.info(f"Chat {self.chat_id} updated successfully.")
            else:
                LOGGER.info(f"Chat {self.chat_id} did not exist and was created with title '{title}'.")
            return True
        except Exception as e:
            LOGGER.error(f"Error updating or inserting chat with ID {self.chat_id}: {e}")
            return False

    async def remove_chat(self) -> bool:
        """Remove a chat document by its ID."""
        try:
            result = await self.collection.delete_one({"_id": self.chat_id})
            if result.deleted_count > 0:
                LOGGER.info(f"Chat {self.chat_id} removed successfully.")
                return True
            LOGGER.warning(f"Chat {self.chat_id} delete found no matching documents.")
            return False
        except PyMongoError as e:
            LOGGER.error(f"Error deleting chat with ID {self.chat_id}: {e}")
            return False

    async def get_all_chats(self, limit: int = 100000) -> List[dict]:
        """Retrieve all chat documents, with an optional limit."""
        try:
            chats = await self.collection.find().limit(limit).to_list(length=limit)
            LOGGER.info(f"Retrieved {len(chats)} chats.")
            return chats
        except PyMongoError as e:
            LOGGER.error(f"Error retrieving all chats: {e}")
            return []
