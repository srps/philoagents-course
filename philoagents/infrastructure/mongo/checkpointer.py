from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver

from philoagents.infrastructure.mongo.utils import get_async_mongo_client
from philoagents.settings import settings

async_mongo_client = get_async_mongo_client()

checkpointer = AsyncMongoDBSaver(
    client=async_mongo_client,
    db_name=settings.MONGO_DB_NAME,
    checkpoint_collection_name=settings.MONGO_STATE_CHECKPOINT_COLLECTION,
    writes_collection_name=settings.MONGO_STATE_WRITES_COLLECTION,
)
