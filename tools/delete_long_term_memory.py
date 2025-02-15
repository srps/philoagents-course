from loguru import logger
from pymongo import MongoClient
from pymongo.database import Database

from philoagents.settings import settings


def delete_rag_collection(
    collection_name: str,
    mongo_uri: str = settings.MONGO_URI,
    db_name: str = settings.MONGO_DB_NAME,
) -> None:
    """Deletes a collection from the specified MongoDB database.

    Args:
        collection_name: Name of the collection to delete.
        mongo_uri: The MongoDB connection URI string. Defaults to local MongoDB instance.
        db_name: The name of the database containing the collection.
                Defaults to 'second_brain'.

    Raises:
        pymongo.errors.ConnectionError: If connection to MongoDB fails.
        pymongo.errors.OperationFailure: If deletion operation fails.
    """

    # Create MongoDB client
    client = MongoClient(mongo_uri)

    # Get database
    db: Database = client[db_name]

    # Delete 'rag' collection if it exists
    if collection_name in db.list_collection_names():
        db.drop_collection(collection_name)
        logger.info(f"Successfully deleted '{collection_name}' collection.")
    else:
        logger.info("'rag' collection does not exist.")

    # Close the connection
    client.close()


if __name__ == "__main__":
    delete_rag_collection(collection_name=settings.MONGO_LONG_TERM_MEMORY_COLLECTION)
