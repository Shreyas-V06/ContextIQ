import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def initialize_db():
    connection_string=os.getenv('CONNECTION_STRING')
    client=MongoClient(connection_string)
    database=client
    return database
