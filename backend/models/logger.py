import os
from enum import Enum
from typing import Dict, Union

from cryptography.fernet import Fernet  # Using Fernet for password encryption
from pymongo import MongoClient
from pymongo.results import InsertOneResult, UpdateResult
from pymongo.errors import DuplicateKeyError


# Set up MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client.pokemon_database
# collection = db.pokemon


class DbCollection(Enum):
    BATTLE = "BATTLE"
    TOURNAMENT = "TOURNAMENT"
    POKEMON = "POKEMON"
    USER = "USER"


class Logger:

    def __init__(self) -> None:
        return

    def log(
        self, data: dict, dbcollection: DbCollection
    ) -> Union[InsertOneResult, UpdateResult, None]:

        if dbcollection == DbCollection.BATTLE:
            collection = "battle"
            filter_query = {"battle id": data["battle id"]}
        elif dbcollection == DbCollection.TOURNAMENT:
            collection = "tournament"
            filter_query = {"tournament id": data["tournament id"]}
        elif dbcollection == DbCollection.POKEMON:
            collection = "pokemon"
            filter_query = {"name": data["name"]}
        elif dbcollection == DbCollection.USER:
            collection = "user"
            data["password"] = self.encrypt_password(data["password"])
            filter_query = {"username": data["username"]}
        else:
            self.admin_log("Improper call to logger")
            return None

        return self.update_or_insert(collection, filter_query, data)

    def encrypt_password(self, password: str) -> str:
        key = os.getenv("ENCRYPTION_KEY")

        if key is None:
            raise ValueError("Encryption key not set in environment variables")

        cipher = Fernet(key)
        encrypted_password = cipher.encrypt(password.encode())
        return encrypted_password

    # admin log is just an array of strings, so simplify by calling directly
    def admin_log(self, message: str) -> int:
        collection = db.admin
        result = collection.update_one(
            {},  # empty filter, should only be one log
            {"$push": {"events": message}},  # append message to running admin event log
        )
        # Will tell us if document was successfully modified
        return result.modified_count

    def update_or_insert(
        self, select: str, filter_query: Dict, data: Dict
    ) -> Union[UpdateResult, InsertOneResult, None]:
        collection = db[select]

        existing_document = collection.find_one(filter_query)

        if existing_document:
            # Perform an update if the document exists
            update_query = {"$set": data}
            result = collection.update_one(filter_query, update_query)
            return result
        else:
            try:
                # Insert a new document if no match is found
                data.update(filter_query)
                result = collection.insert_one(data)
                return result
            except DuplicateKeyError:
                self.admin_log(
                    f"Duplicate key error: A document with {filter_query} already exists."
                )
                return None
