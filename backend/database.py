# backend/database.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://root:example@mongo:27017")
client = MongoClient(MONGO_URI)
db = client["marine_db"]
