"""MongoDB database configuration and connection management."""
import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

def is_db_enabled() -> bool:
    """Check if MongoDB is enabled via environment variable."""
    return os.getenv("ENABLE_MONGODB", "false").lower() == "true"

# Only import motor if MongoDB is enabled
if is_db_enabled():
    from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

class Database:
    client: Optional["AsyncIOMotorClient"] = None
    db: Optional["AsyncIOMotorDatabase"] = None

async def connect_db():
    """Create database connection."""
    if not is_db_enabled():
        print("MongoDB is disabled (ENABLE_MONGODB != 'true')")
        return

    from motor.motor_asyncio import AsyncIOMotorClient
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    Database.client = AsyncIOMotorClient(mongodb_url)
    Database.db = Database.client.get_database("videre")
    print(f"Connected to MongoDB at {mongodb_url}")

async def close_db():
    """Close database connection."""
    if not is_db_enabled():
        return
    if Database.client:
        Database.client.close()
        print("Closed MongoDB connection")

def get_database() -> "AsyncIOMotorDatabase":
    """Get database instance."""
    if not is_db_enabled():
        raise RuntimeError("MongoDB is disabled. Set ENABLE_MONGODB=true to use database features.")
    if Database.db is None:
        raise RuntimeError("Database not initialized. Call connect_db() first.")
    return Database.db
