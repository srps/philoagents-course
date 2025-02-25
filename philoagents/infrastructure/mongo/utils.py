from typing import Any, Dict, Optional

from pymongo import AsyncMongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from philoagents.settings import settings


# TODO: This is a quick hack to get the mongo client. Build a proper dependency injection system.
def get_mongo_client() -> MongoClient:
    """
    Creates and returns a MongoDB client instance.

    Returns:
        MongoClient: Configured MongoDB client
    """
    client = MongoClient(settings.MONGO_URI, server_api=ServerApi("1"))
    return client


def get_async_mongo_client() -> AsyncMongoClient:
    """
    Creates and returns a MongoDB client instance.

    Returns:
        MongoClient: Configured MongoDB client
    """
    client = AsyncMongoClient(settings.MONGO_URI)
    return client


def get_database(client: MongoClient, db_name: Optional[str] = None) -> Database:
    """
    Gets a MongoDB database instance.

    Args:
        client (MongoClient): MongoDB client instance
        db_name (Optional[str]): Database name, defaults to settings.MONGO_DB_NAME

    Returns:
        Database: MongoDB database instance
    """
    return client[db_name or settings.MONGO_DB_NAME]


def get_collection(db: Database, collection_name: str) -> Collection:
    """
    Gets a MongoDB collection instance.

    Args:
        db (Database): MongoDB database instance
        collection_name (str): Name of the collection

    Returns:
        Collection: MongoDB collection instance
    """
    return db[collection_name]


def save_document(
    collection: Collection, document: Dict[str, Any], id_field: str = "_id"
) -> None:
    """
    Saves or updates a document in the specified collection.

    Args:
        collection (Collection): MongoDB collection instance
        document (Dict[str, Any]): Document to save
        id_field (str): Field to use as document ID, defaults to "_id"

    Raises:
        ValueError: If document doesn't contain id_field
    """
    if id_field not in document:
        raise ValueError(f"Document must contain {id_field} field")

    collection.update_one(
        {id_field: document[id_field]}, {"$set": document}, upsert=True
    )


def get_document(
    collection: Collection, id_value: Any, id_field: str = "_id"
) -> Dict[str, Any]:
    """
    Retrieves a document from the specified collection.

    Args:
        collection (Collection): MongoDB collection instance
        id_value (Any): Value of the ID field to search for
        id_field (str): Field to use as document ID, defaults to "_id"

    Returns:
        Dict[str, Any]: Retrieved document

    Raises:
        ValueError: If document is not found
    """
    document = collection.find_one({id_field: id_value})
    if not document:
        raise ValueError(f"No document found with {id_field}: {id_value}")
    return document


def delete_document(
    collection: Collection, id_value: Any, id_field: str = "_id"
) -> None:
    """
    Deletes a document from the specified collection.

    Args:
        collection (Collection): MongoDB collection instance
        id_value (Any): Value of the ID field to delete
        id_field (str): Field to use as document ID, defaults to "_id"

    Raises:
        ValueError: If document is not found
    """
    result = collection.delete_one({id_field: id_value})
    if result.deleted_count == 0:
        raise ValueError(f"No document found with {id_field}: {id_value}")
