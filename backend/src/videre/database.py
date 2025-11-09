"""MongoDB database configuration and connection management."""
import os
from typing import Optional

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

load_dotenv()

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

async def connect_db():
    """Create database connection."""
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    Database.client = AsyncIOMotorClient(mongodb_url)
    Database.db = Database.client.get_database("videre")
    print(f"Connected to MongoDB at {mongodb_url}")

async def close_db():
    """Close database connection."""
    if Database.client:
        Database.client.close()
        print("Closed MongoDB connection")

def get_database() -> AsyncIOMotorDatabase:
    """Get database instance."""
    if Database.db is None:
        raise RuntimeError("Database not initialized. Call connect_db() first.")
    return Database.db
