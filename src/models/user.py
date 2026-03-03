"""
Modèle User pour MongoDB
"""
from datetime import datetime
from bson import ObjectId
from src.models.database import get_db

class User:
    """Classe pour gérer les utilisateurs"""
    
    @staticmethod
    def create(data):
        """Crée un nouvel utilisateur"""
        db = get_db()
        data['date_inscription'] = datetime.utcnow()
        data['actif'] = data.get('actif', True)
        data['role'] = data.get('role', 'client')
        result = db.users.insert_one(data)
        return result.inserted_id
    
    @staticmethod
    def get_by_id(user_id):
        """Récupère un utilisateur par son ID"""
        db = get_db()
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            user['_id'] = str(user['_id'])
        return user
    
    @staticmethod
    def get_by_email(email):
        """Récupère un utilisateur par son email"""
        db = get_db()
        user = db.users.find_one({"email": email})
        if user:
            user['_id'] = str(user['_id'])
        return user
    
    @staticmethod
    def update(user_id, data):
        """Met à jour un utilisateur"""
        db = get_db()
        result = db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def get_all(role=None, limit=None, skip=0):
        """Récupère tous les utilisateurs"""
        db = get_db()
        query = {}
        if role:
            query['role'] = role
        
        cursor = db.users.find(query).sort("date_inscription", -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        users = list(cursor)
        for user in users:
            user['_id'] = str(user['_id'])
        
        return users


