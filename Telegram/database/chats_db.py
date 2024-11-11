from typing import Optional

from pymongo.errors import PyMongoError

from . import mongo
from .. import LOGGER


class ChatsDB:
    collection_name = "Chats"

    def __init__(self, chat_id: int) -> None:
        """
        Initialize the Chats class with a specific MongoDB collection.

        :param chat_id: Unique identifier for the chat.
        """
        self.collection = mongo.db[self.collection_name]
        self.chat_id = chat_id

    async def get_chat(self) -> Optional[dict]:
        """
        Retrieve a single chat document by its ID.

        :return: Chat document if found, otherwise None.
        """
        try:
            return await self.collection.find_one({"_id": self.chat_id})
        except PyMongoError as e:
            LOGGER.error(f"Error retrieving chat with ID {self.chat_id}: {e}")
            return None

    async def update_chat(self, title: str, username: str) -> bool:
        """
        Update the title and username of a specific chat, or insert if it doesn't exist.

        :param title: Title of the chat.
        :param username: Username of the chat.
        :return: True if the operation was successful, False otherwise.
        """
        try:
            result = await self.collection.update_one(
                {"_id": self.chat_id},
                {"$set": {"title": title, "username": username}},
                upsert=True,
            )
            if result.matched_count > 0:
                LOGGER.info(
                    f"Chat {self.chat_id} updated successfully with title '{title}' and username '{username}'."
                )
            else:
                LOGGER.info(
                    f"Chat {self.chat_id} created with title '{title}' and username '{username}'."
                )
            return True
        except PyMongoError as e:
            LOGGER.error(
                f"Error updating or inserting chat with ID {self.chat_id}: {e}"
            )
            return False

    async def remove_chat(self) -> bool:
        """
        Remove a chat document by its ID.

        :return: True if deletion was successful, False if no matching document was found.
        """
        try:
            result = await self.collection.delete_one({"_id": self.chat_id})
            if result.deleted_count > 0:
                LOGGER.info(f"Chat {self.chat_id} removed successfully.")
                return True
            LOGGER.warning(f"No chat found for deletion with ID {self.chat_id}.")
            return False
        except PyMongoError as e:
            LOGGER.error(f"Error deleting chat with ID {self.chat_id}: {e}")
            return False

    async def get_all_chats(self, limit: int = 100000) -> list[dict]:
        """
        Retrieve all chat documents, with an optional limit.

        :param limit: Maximum number of chat documents to retrieve.
        :return: List of chat documents.
        """
        try:
            chats = await self.collection.find().limit(limit).to_list(length=limit)
            LOGGER.info(f"Retrieved {len(chats)} chats.")
            return chats
        except PyMongoError as e:
            LOGGER.error(f"Error retrieving all chats: {e}")
            return []
