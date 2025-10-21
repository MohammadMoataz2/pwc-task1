import motor.motor_asyncio
from beanie import init_beanie
from pwc.settings import settings
from pwc.logger import setup_logger
from ..db.models import Contract, Client, User, LogEntry, MetricEntry, PromptTemplate

logger = setup_logger(__name__)


async def init_database():
    """Initialize MongoDB connection and Beanie ODM"""
    try:
        # Create Motor client
        client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_url)
        database = client[settings.mongodb_database]

        # Initialize Beanie with document models
        await init_beanie(
            database=database,
            document_models=[
                Contract,
                Client,
                User,
                LogEntry,
                MetricEntry,
                PromptTemplate
            ]
        )

        logger.info(f"Connected to MongoDB: {settings.mongodb_database}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_database():
    """Close database connections"""
    logger.info("Closing database connections")