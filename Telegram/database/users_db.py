from typing import Optional, List, Union

from pymongo.errors import PyMongoError

from . import mongo
from .. import LOGGER


class Users:
    collection_name = "users"

    def __init__(self, user_id: int) -> None:
        """
        Initialize the Users class with a specific MongoDB collection.
        """
        self.collection = mongo.db[self.collection_name]
        self.user_id = user_id or 0

    @classmethod
    async def get_user_info(cls, user: Union[int, str]) -> \
    Optional[dict]:
        """
        Retrieve user information based on user ID or username.

        :param user: Either the user ID (int) or username (str).
        :return: User document if found, otherwise None.
        """
        collection = mongo.db[cls.collection_name]

        # Prepare the query based on user type
        if isinstance(user, int):
            query = {"_id": user}
        elif isinstance(user, str):
            # Remove '@' if present at the start of the username
            query = {"username": user.lstrip('@')}
        else:
            LOGGER.warning("Invalid type for 'user' argument; expected int or str.")
            return None

        try:
            user_info = await collection.find_one(query)
            if user_info:
                LOGGER.info(f"Retrieved user info for {'ID' if isinstance(user, int) else 'username'} '{user}'.")
            else:
                LOGGER.warning(f"No user found for {'ID' if isinstance(user, int) else 'username'} '{user}'.")
            return user_info or {}
        except PyMongoError as e:
            LOGGER.error(
                f"Error retrieving user info for {'ID' if isinstance(user, int) else 'username'} '{user}': {e}")
            return None

    async def get_user(self) -> Optional[dict]:
        """Retrieve a single user document by its ID."""
        try:
            user = await self.collection.find_one({"_id": self.user_id})
            return user
        except Exception as e:
            LOGGER.error(f"Error retrieving user with ID {self.user_id}: {e}")
            return None

    async def update_user(self, full_name: str, username: str, pm: bool) -> bool:
        """Update the fullName, username, and pm status of a user, or insert if it doesn't exist."""
        try:
            result = await self.collection.update_one(
                {"_id": self.user_id},
                {"$set": {"fullName": full_name, "username": username, "pm": pm}},
                upsert=True,
            )
            if result.matched_count > 0:
                LOGGER.info(f"User {self.user_id} updated successfully.")
            else:
                LOGGER.info(f"User {self.user_id} did not exist and was created with fullName '{full_name}', username '{username}', and pm={pm}.")
            return True
        except Exception as e:
            LOGGER.error(f"Error updating or inserting user with ID {self.user_id}: {e}")
            return False

    async def remove_user(self) -> bool:
        """Remove a user document by its ID."""
        try:
            result = await self.collection.delete_one({"_id": self.user_id})
            if result.deleted_count > 0:
                LOGGER.info(f"User {self.user_id} removed successfully.")
                return True
            LOGGER.warning(f"User {self.user_id} delete found no matching documents.")
            return False
        except PyMongoError as e:
            LOGGER.error(f"Error deleting user with ID {self.user_id}: {e}")
            return False

    async def get_all_users(self, limit: int = 100000) -> List[dict]:
        """Retrieve all user documents, with an optional limit."""
        try:
            users = await self.collection.find().limit(limit).to_list(length=limit)
            LOGGER.info(f"Retrieved {len(users)} users.")
            return users
        except PyMongoError as e:
            LOGGER.error(f"Error retrieving all users: {e}")
            return []
