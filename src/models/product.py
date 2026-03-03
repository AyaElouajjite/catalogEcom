"""
Modèle Product pour MongoDB
"""
from datetime import datetime
from bson import ObjectId
from src.models.database import get_db

class Product:
    """Classe pour gérer les produits"""
    
    @staticmethod
    def create(data):
        """Crée un nouveau produit"""
        db = get_db()
        data['date_creation'] = datetime.utcnow()
        data['date_modification'] = datetime.utcnow()
        result = db.products.insert_one(data)
        return result.inserted_id
    
    @staticmethod
    def get_by_id(product_id):
        """Récupère un produit par son ID"""
        db = get_db()
        product = db.products.find_one({"_id": ObjectId(product_id)})
        if product:
            product['_id'] = str(product['_id'])
            if 'categorie_id' in product and product['categorie_id']:
                product['categorie_id'] = str(product['categorie_id'])
        return product
    
    @staticmethod
    def get_all(filters=None, limit=None, skip=0):
        """Récupère tous les produits avec filtres optionnels"""
        db = get_db()
        query = {}
        if filters:
            query = filters.copy()
            # Convertir les ObjectId dans les filtres
            if 'categorie_id' in query and isinstance(query['categorie_id'], str):
                query['categorie_id'] = ObjectId(query['categorie_id'])
            if '_id' in query:
                if isinstance(query['_id'], dict) and '$ne' in query['_id']:
                    query['_id']['$ne'] = ObjectId(query['_id']['$ne'])
                elif isinstance(query['_id'], str):
                    query['_id'] = ObjectId(query['_id'])
        
        cursor = db.products.find(query).sort("date_creation", -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        products = list(cursor)
        for product in products:
            product['_id'] = str(product['_id'])
            if 'categorie_id' in product and product['categorie_id']:
                product['categorie_id'] = str(product['categorie_id'])
        
        return products
    
    @staticmethod
    def update(product_id, data):
        """Met à jour un produit"""
        db = get_db()
        data['date_modification'] = datetime.utcnow()
        result = db.products.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def delete(product_id):
        """Supprime un produit"""
        db = get_db()
        result = db.products.delete_one({"_id": ObjectId(product_id)})
        return result.deleted_count > 0
    
    @staticmethod
    def search(query_text, filters=None):
        """Recherche de produits par texte"""
        db = get_db()
        search_query = {"$text": {"$search": query_text}}
        if filters:
            search_query.update(filters)
            # Convertir les ObjectId dans les filtres
            if 'categorie_id' in search_query and isinstance(search_query['categorie_id'], str):
                search_query['categorie_id'] = ObjectId(search_query['categorie_id'])
        
        products = list(db.products.find(search_query))
        for product in products:
            product['_id'] = str(product['_id'])
            if 'categorie_id' in product and product['categorie_id']:
                product['categorie_id'] = str(product['categorie_id'])
        
        return products
    
    @staticmethod
    def get_variation(product_id, variation_id):
        """Récupère une variation spécifique d'un produit"""
        product = Product.get_by_id(product_id)
        if not product or 'variations' not in product:
            return None
        
        for variation in product['variations']:
            var_id = variation.get('_id')
            # Gérer les cas où _id est déjà un string ou un ObjectId
            if isinstance(var_id, str):
                if var_id == str(variation_id):
                    return variation
            else:
                # Convertir en string pour comparaison
                if str(var_id) == str(variation_id):
                    variation['_id'] = str(variation['_id'])
                    return variation
        
        return None

    @staticmethod
    def decrement_stock(product_id, variation_id=None, delta=-1):
        """
        Décrémente le stock d'un produit ou d'une variation.
        delta doit être négatif pour décrémenter, positif pour récréditer.
        """
        db = get_db()
        try:
            pid = ObjectId(product_id)
        except Exception:
            return False

        if variation_id:
            try:
                vid = ObjectId(variation_id)
            except Exception:
                return False
            # Mettre à jour la variation dans le tableau variations
            result = db.products.update_one(
                {"_id": pid, "variations._id": vid},
                {"$inc": {"variations.$.stock": delta}}
            )
            return result.modified_count > 0
        else:
            # Si on stocke un stock global sur le produit (optionnel)
            result = db.products.update_one(
                {"_id": pid},
                {"$inc": {"stock": delta}}
            )
            return result.modified_count > 0

