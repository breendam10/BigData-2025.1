# C:\Users\ianes\Desktop\BigData-2025.1\app\config.py
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY")

    # Config do MySQL
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Config do Cosmos
    COSMOS_ENDPOINT = os.environ.get("COSMOS_ENDPOINT")
    COSMOS_KEY = os.environ.get("COSMOS_KEY")
    COSMOS_DATABASE_NAME = os.environ.get("COSMOS_DB_NAME")
    COSMOS_CONTAINER_NAME = os.environ.get("COSMOS_CONTAINER_NAME")
