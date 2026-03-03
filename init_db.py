"""
Script d'initialisation de la base de données MongoDB
Crée les collections et un compte administrateur par défaut
"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from src.utils.auth import hash_password

load_dotenv()

def init_database():
    """Initialise la base de données avec les collections et données par défaut"""
    mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    db_name = os.getenv('DATABASE_NAME', 'ecommerce_db')
    
    client = MongoClient(mongodb_uri)
    db = client[db_name]
    
    # Créer les index
    print("Création des index...")
    
    # Index pour users
    db.users.create_index("email", unique=True)
    db.users.create_index("role")
    
    # Index pour products
    db.products.create_index("categorie_id")
    db.products.create_index("publie")
    db.products.create_index([("nom", "text"), ("description", "text")])
    
    # Index pour orders
    db.orders.create_index("client_id")
    db.orders.create_index("numero_commande", unique=True)
    db.orders.create_index("statut")
    db.orders.create_index("date_commande")
    
    # Index pour categories
    db.categories.create_index("slug", unique=True)
    
    # Créer un admin par défaut si n'existe pas
    admin_exists = db.users.find_one({"email": "admin@example.com"})
    if not admin_exists:
        print("Création du compte administrateur par défaut...")
        admin = {
            "email": "admin@example.com",
            "password_hash": hash_password("admin123"),
            "role": "admin",
            "nom": "Admin",
            "prenom": "Système",
            "adresse": {},
            "telephone": "",
            "date_inscription": None,
            "actif": True
        }
        db.users.insert_one(admin)
        print("✓ Compte admin créé: admin@example.com / admin123")
    else:
        print("✓ Compte admin existe déjà")
    
    # Créer quelques catégories par défaut
    categories = [
        {"nom": "Vêtements", "slug": "vetements", "description": "Vêtements et accessoires"},
        {"nom": "Chaussures", "slug": "chaussures", "description": "Chaussures et baskets"},
        {"nom": "Électronique", "slug": "electronique", "description": "Appareils électroniques"},
        {"nom": "Maison", "slug": "maison", "description": "Décoration et mobilier"}
    ]
    
    for cat in categories:
        existing = db.categories.find_one({"slug": cat["slug"]})
        if not existing:
            db.categories.insert_one(cat)
            print(f"✓ Catégorie créée: {cat['nom']}")
    
    print("\n✓ Base de données initialisée avec succès!")
    print(f"✓ Base de données: {db_name}")
    client.close()

if __name__ == "__main__":
    init_database()


