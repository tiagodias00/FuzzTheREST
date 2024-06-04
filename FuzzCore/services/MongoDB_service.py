import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv()

class MongoDBService:
    def __init__(self):
        self.mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        self.db_name = os.getenv('MONGO_DB_NAME')
        self.collection_name = os.getenv('MONGO_COLLECTION_NAME', 'metrics')
        self.client = None
        self.db = None
        self.collection = None

    def connect(self):
        if not self.client:
            try:
                self.client = MongoClient(self.mongo_uri)
                self.db = self.client[self.db_name]
                self.collection = self.db[self.collection_name]
            except PyMongoError as e:
                print(f"MongoDB connection error: {e}")
                self.client = None

    def save_metrics(self, key, data):
        if not self.client:
            self.connect()
        if self.client:
            try:
                document = {"_id": key, "data": data}
                result = self.collection.update_one(
                    {"_id": key},
                    {"$set": document},
                    upsert=True
                )
                return result.acknowledged
            except PyMongoError as e:
                print(f"MongoDB error: {e}")
                return False

