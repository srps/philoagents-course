from typing import Optional
from loguru import logger
from pymongo import MongoClient

from philoagents.config import settings


async def reset_conversation_state(user_id: Optional[str] = None) -> dict:
    """Deletes conversation state data from MongoDB.

    This function removes stored conversation checkpoints and writes.
    If user_id is provided, only removes data for that specific user.
    If user_id is None, removes all conversation data.

    Args:
        user_id: Optional user identifier to reset specific user's conversations

    Returns:
        dict: Status message indicating success or failure with details
              about which data was deleted

    Raises:
        Exception: If there's an error connecting to MongoDB or deleting data
    """
    try:
        client = MongoClient(settings.MONGO_URI)
        db = client[settings.MONGO_DB_NAME]

        deleted_count = 0
        collections_affected = []

        if user_id:
            # Delete only documents for the specific user
            # Thread IDs are in format "user_id:philosopher_id"
            thread_pattern = {"thread_id": {"$regex": f"^{user_id}:"}}

            if settings.MONGO_STATE_CHECKPOINT_COLLECTION in db.list_collection_names():
                checkpoint_collection = db[settings.MONGO_STATE_CHECKPOINT_COLLECTION]
                result = checkpoint_collection.delete_many(thread_pattern)
                deleted_count += result.deleted_count
                if result.deleted_count > 0:
                    collections_affected.append(f"{settings.MONGO_STATE_CHECKPOINT_COLLECTION} ({result.deleted_count} documents)")
                logger.info(f"Deleted {result.deleted_count} checkpoint documents for user {user_id}")

            if settings.MONGO_STATE_WRITES_COLLECTION in db.list_collection_names():
                writes_collection = db[settings.MONGO_STATE_WRITES_COLLECTION]
                result = writes_collection.delete_many(thread_pattern)
                deleted_count += result.deleted_count
                if result.deleted_count > 0:
                    collections_affected.append(f"{settings.MONGO_STATE_WRITES_COLLECTION} ({result.deleted_count} documents)")
                logger.info(f"Deleted {result.deleted_count} writes documents for user {user_id}")

            message = f"Successfully deleted {deleted_count} documents for user {user_id}"
            if collections_affected:
                message += f" from: {', '.join(collections_affected)}"
        else:
            # Delete all collections (original behavior)
            collections_deleted = []

            if settings.MONGO_STATE_CHECKPOINT_COLLECTION in db.list_collection_names():
                db.drop_collection(settings.MONGO_STATE_CHECKPOINT_COLLECTION)
                collections_deleted.append(settings.MONGO_STATE_CHECKPOINT_COLLECTION)
                logger.info(f"Deleted collection: {settings.MONGO_STATE_CHECKPOINT_COLLECTION}")

            if settings.MONGO_STATE_WRITES_COLLECTION in db.list_collection_names():
                db.drop_collection(settings.MONGO_STATE_WRITES_COLLECTION)
                collections_deleted.append(settings.MONGO_STATE_WRITES_COLLECTION)
                logger.info(f"Deleted collection: {settings.MONGO_STATE_WRITES_COLLECTION}")

            if collections_deleted:
                message = f"Successfully deleted collections: {', '.join(collections_deleted)}"
            else:
                message = "No collections needed to be deleted"

        client.close()

        return {
            "status": "success",
            "message": message,
        }

    except Exception as e:
        logger.error(f"Failed to reset conversation state: {str(e)}")
        raise Exception(f"Failed to reset conversation state: {str(e)}")
