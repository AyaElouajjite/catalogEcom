"""
Modèle Order pour MongoDB
"""
from datetime import datetime
from bson import ObjectId
from src.models.database import get_db

class Order:
    """Classe pour gérer les commandes"""
    
    @staticmethod
    def generate_order_number():
        """Génère un numéro de commande unique"""
        db = get_db()
        today = datetime.utcnow().strftime("%Y%m%d")
        count = db.orders.count_documents({
            "numero_commande": {"$regex": f"CMD-{today}"}
        })
        return f"CMD-{today}-{str(count + 1).zfill(5)}"
    
    @staticmethod
    def create(data):
        """Crée une nouvelle commande"""
        db = get_db()
        data['numero_commande'] = Order.generate_order_number()
        data['date_commande'] = datetime.utcnow()
        data['statut'] = data.get('statut', 'en_attente')
        
        result = db.orders.insert_one(data)
        return result.inserted_id
    
    @staticmethod
    def get_by_id(order_id):
        """Récupère une commande par son ID"""
        db = get_db()
        order = db.orders.find_one({"_id": ObjectId(order_id)})
        if order:
            order['_id'] = str(order['_id'])
            if 'client_id' in order and order['client_id']:
                order['client_id'] = str(order['client_id'])
        return order
    
    @staticmethod
    def get_by_client(client_id, limit=None):
        """Récupère les commandes d'un client"""
        db = get_db()
        query = {"client_id": ObjectId(client_id)}
        cursor = db.orders.find(query).sort("date_commande", -1)
        if limit:
            cursor = cursor.limit(limit)
        
        orders = list(cursor)
        for order in orders:
            order['_id'] = str(order['_id'])
            order['client_id'] = str(order['client_id'])
        
        return orders
    
    @staticmethod
    def get_all(filters=None, limit=None, skip=0):
        """Récupère toutes les commandes"""
        db = get_db()
        query = filters or {}
        
        cursor = db.orders.find(query).sort("date_commande", -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        orders = list(cursor)
        for order in orders:
            order['_id'] = str(order['_id'])
            if 'client_id' in order and order['client_id']:
                order['client_id'] = str(order['client_id'])
        
        return orders
    
    @staticmethod
    def update_status(order_id, new_status):
        """Met à jour le statut d'une commande"""
        db = get_db()
        update_data = {"statut": new_status}
        
        if new_status == 'payee':
            update_data['date_paiement'] = datetime.utcnow()
        
        result = db.orders.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0


