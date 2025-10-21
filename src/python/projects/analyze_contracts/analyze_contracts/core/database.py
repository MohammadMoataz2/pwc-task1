import motor.motor_asyncio
from beanie import init_beanie
from pwc.settings import settings
from pwc.logger import setup_logger

logger = setup_logger(__name__)

# Import models needed for worker
from pwc.task_interface import ContractDocument


class WorkerDatabase:
    """Database connection for worker"""

    def __init__(self):
        self.client = None
        self.database = None

    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_url)
            self.database = self.client[settings.mongodb_database]

            # Initialize Beanie with minimal models needed for worker
            await init_beanie(
                database=self.database,
                document_models=[ContractDocument]
            )

            logger.info(f"Worker connected to MongoDB: {settings.mongodb_database}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Worker database connection closed")


# Global database instance
worker_db = WorkerDatabase()