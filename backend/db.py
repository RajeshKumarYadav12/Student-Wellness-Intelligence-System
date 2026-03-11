"""
MongoDB Motor client for async database operations.
Database: aura_db
Collections: behavioral_logs, risk_predictions, identity_vault, students
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

# MongoDB connection string from environment
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/aura_db')
DB_NAME = 'aura_db'

# Global client instance
client: Optional[AsyncIOMotorClient] = None


def get_database():
    """Get the aura_db database instance."""
    global client
    if client is None:
        client = AsyncIOMotorClient(MONGO_URI)
    return client[DB_NAME]


def get_db():
    """FastAPI dependency for database access."""
    return get_database()


async def close_db_connection():
    """Close MongoDB connection (called on app shutdown)."""
    global client
    if client is not None:
        client.close()
        client = None
