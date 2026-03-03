"""
Script de diagnostic pour vérifier les images des produits
"""
import os
from src.models.database import get_db
from src.models.product import Product

def check_images():
    """Vérifie les images des produits"""
    db = get_db()
    products = Product.get_all()
    
    print("=== Diagnostic des images ===\n")
    
    for product in products:
        print(f"Produit: {product.get('nom', 'N/A')}")
        print(f"  ID: {product.get('_id', 'N/A')}")
        
        images = product.get('images_principales', [])
        print(f"  Nombre d'images: {len(images)}")
        
        if images:
            for i, image_path in enumerate(images):
                # Chemin complet attendu
                full_path = os.path.join('static', 'images', image_path)
                exists = os.path.exists(full_path)
                
                print(f"  Image {i+1}: {image_path}")
                print(f"    Chemin complet: {full_path}")
                print(f"    Existe: {'✓' if exists else '✗'}")
                
                if not exists:
                    # Essayer de trouver le fichier
                    if os.path.exists(os.path.join('static', 'images', 'uploads', os.path.basename(image_path))):
                        print(f"    ⚠ Trouvé dans uploads/ mais chemin incorrect dans DB")
        else:
            print("  ⚠ Aucune image")
        
        print()

if __name__ == '__main__':
    check_images()

