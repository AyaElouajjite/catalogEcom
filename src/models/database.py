"""
Configuration et connexion à MongoDB
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Configuration MongoDB
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'ecommerce_db')

# Client MongoDB global
_client = None
_db = None

def get_client():
    """Retourne le client MongoDB"""
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URI)
    return _client

def get_db():
    """Retourne la base de données"""
    global _db
    if _db is None:
        client = get_client()
        _db = client[DATABASE_NAME]
    return _db

def close_db():
    """Ferme la connexion MongoDB"""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None


