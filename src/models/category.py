"""
Modèle Category pour MongoDB
"""
from bson import ObjectId
from src.models.database import get_db

class Category:
    """Classe pour gérer les catégories"""
    
    @staticmethod
    def create(data):
        """Crée une nouvelle catégorie"""
        db = get_db()
        result = db.categories.insert_one(data)
        return result.inserted_id
    
    @staticmethod
    def get_by_id(category_id):
        """Récupère une catégorie par son ID"""
        db = get_db()
        category = db.categories.find_one({"_id": ObjectId(category_id)})
        if category:
            category['_id'] = str(category['_id'])
        return category
    
    @staticmethod
    def get_by_slug(slug):
        """Récupère une catégorie par son slug"""
        db = get_db()
        category = db.categories.find_one({"slug": slug})
        if category:
            category['_id'] = str(category['_id'])
        return category
    
    @staticmethod
    def get_all():
        """Récupère toutes les catégories"""
        db = get_db()
        categories = list(db.categories.find().sort("nom", 1))
        for category in categories:
            category['_id'] = str(category['_id'])
        return categories
    
    @staticmethod
    def update(category_id, data):
        """Met à jour une catégorie"""
        db = get_db()
        result = db.categories.update_one(
            {"_id": ObjectId(category_id)},
            {"$set": data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def delete(category_id):
        """Supprime une catégorie"""
        db = get_db()
        result = db.categories.delete_one({"_id": ObjectId(category_id)})
        return result.deleted_count > 0


