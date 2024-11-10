from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO


class MongoDB:
    def __init__(self):
        """Initialize the MongoDB client."""
        if not MONGO:
            raise SystemExit(
                "MONGO environment variable is not configured. Please set it to connect to the database."
            )

        self.client = AsyncIOMotorClient(MONGO)
        self.db = self.client.TelegramTest

    async def connect(self) -> None:
        """Check if we can connect to the database.

        Raises:
            SystemExit: If the connection to the database fails.
        """
        try:
            await self.client.admin.command("ping")
            print("Successfully connected to the database.")
        except Exception as e:
            raise SystemExit(f"Database connection failed: {e}") from e

    async def close(self) -> None:
        """Close the MongoDB connection."""
        self.client.close()


mongo = MongoDB()

__all__ = ["mongo"]
