"""
Routes administrateur
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from src.utils.auth import admin_required
from src.models.product import Product
from src.models.category import Category
from src.models.order import Order
from src.models.user import User
from bson import ObjectId
import os
from datetime import datetime

bp = Blueprint('admin', __name__, url_prefix='/admin')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
@admin_required
def dashboard():
    """Dashboard administrateur"""
    from src.models.database import get_db
    
    db = get_db()
    
    # Statistiques
    stats = {
        'total_products': db.products.count_documents({}),
        'published_products': db.products.count_documents({"publie": True}),
        'total_orders': db.orders.count_documents({}),
        'pending_orders': db.orders.count_documents({"statut": "en_attente"}),
        'total_users': db.users.count_documents({"role": "client"}),
        'total_categories': db.categories.count_documents({})
    }
    
    # Commandes récentes
    recent_orders = Order.get_all(limit=10)
    
    return render_template('admin/dashboard.html', stats=stats, recent_orders=recent_orders)

# ========== GESTION PRODUITS ==========

@bp.route('/produits')
@admin_required
def products_list():
    """Liste des produits"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    skip = (page - 1) * per_page
    
    products = Product.get_all(limit=per_page, skip=skip)
    categories = Category.get_all()
    
    return render_template('admin/products/list.html', products=products, categories=categories, page=page)

@bp.route('/produits/nouveau', methods=['GET', 'POST'])
@admin_required
def product_add():
    """Ajouter un produit"""
    if request.method == 'POST':
        # Récupérer les données du formulaire
        data = {
            'nom': request.form.get('nom', '').strip(),
            'description': request.form.get('description', '').strip(),
            'categorie_id': request.form.get('categorie_id') if request.form.get('categorie_id') else None,
            'marque': request.form.get('marque', '').strip(),
            'prix_base': float(request.form.get('prix_base', 0)),
            'publie': request.form.get('publie') == 'on',
            'images_principales': [],
            'variations': [],
            'caracteristiques': []
        }
        
        # Convertir categorie_id en ObjectId si fourni
        if data['categorie_id']:
            data['categorie_id'] = ObjectId(data['categorie_id'])
        
        # Gérer les attributs config
        attributs_config = {}
        attribut_names = request.form.getlist('attribut_name[]')
        attribut_values = request.form.getlist('attribut_values[]')
        
        for name, values_str in zip(attribut_names, attribut_values):
            if name and values_str:
                values = [v.strip() for v in values_str.split(',') if v.strip()]
                if values:
                    attributs_config[name] = values
        
        data['attributs_config'] = attributs_config
        
        # Générer les variations
        if attributs_config:
            from itertools import product
            keys = list(attributs_config.keys())
            values = list(attributs_config.values())
            
            for combo in product(*values):
                variation_attrs = dict(zip(keys, combo))
                sku = f"{data['nom'][:3].upper()}-{'-'.join([str(v)[:3].upper() for v in combo])}"
                
                variation = {
                    '_id': ObjectId(),
                    'sku': sku,
                    'attributs': variation_attrs,
                    'prix': data['prix_base'],
                    'stock': 0,
                    'images': [],
                    'actif': True
                }
                data['variations'].append(variation)
        
        # Upload images
        if 'images' in request.files:
            files = request.files.getlist('images')
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = timestamp + filename
                    filepath = os.path.join('static/images/uploads', filename)
                    file.save(filepath)
                    data['images_principales'].append(f'uploads/{filename}')
        
        product_id = Product.create(data)
        flash('Produit créé avec succès', 'success')
        return redirect(url_for('admin.product_edit', product_id=str(product_id)))
    
    categories = Category.get_all()
    return render_template('admin/products/add.html', categories=categories)

@bp.route('/produits/<product_id>/edit', methods=['GET', 'POST'])
@admin_required
def product_edit(product_id):
    """Modifier un produit"""
    product = Product.get_by_id(product_id)
    if not product:
        flash('Produit introuvable', 'error')
        return redirect(url_for('admin.products_list'))
    
    if request.method == 'POST':
        data = {
            'nom': request.form.get('nom', '').strip(),
            'description': request.form.get('description', '').strip(),
            'categorie_id': request.form.get('categorie_id') if request.form.get('categorie_id') else None,
            'marque': request.form.get('marque', '').strip(),
            'prix_base': float(request.form.get('prix_base', 0)),
            'publie': request.form.get('publie') == 'on'
        }
        
        # Convertir categorie_id en ObjectId si fourni
        if data['categorie_id']:
            data['categorie_id'] = ObjectId(data['categorie_id'])
        
        # Mettre à jour les variations
        if 'variations' in product:
            variations = []
            variation_ids = request.form.getlist('variation_id[]')
            variation_prices = request.form.getlist('variation_price[]')
            variation_stocks = request.form.getlist('variation_stock[]')
            
            for i, var_id in enumerate(variation_ids):
                if var_id:
                    # Trouver la variation originale
                    original_var = None
                    for var in product.get('variations', []):
                        if str(var.get('_id')) == var_id:
                            original_var = var
                            break
                    
                    if original_var:
                        variation = original_var.copy()
                        variation['prix'] = float(variation_prices[i]) if i < len(variation_prices) else variation.get('prix', 0)
                        variation['stock'] = int(variation_stocks[i]) if i < len(variation_stocks) else variation.get('stock', 0)
                        variations.append(variation)
            
            data['variations'] = variations
        
        # Upload nouvelles images
        if 'images' in request.files:
            files = request.files.getlist('images')
            existing_images = product.get('images_principales', [])
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = timestamp + filename
                    filepath = os.path.join('static/images/uploads', filename)
                    file.save(filepath)
                    existing_images.append(f'uploads/{filename}')
            data['images_principales'] = existing_images
        
        Product.update(product_id, data)
        flash('Produit mis à jour avec succès', 'success')
        return redirect(url_for('admin.product_edit', product_id=product_id))
    
    categories = Category.get_all()
    return render_template('admin/products/edit.html', product=product, categories=categories)

@bp.route('/produits/<product_id>/delete', methods=['POST'])
@admin_required
def product_delete(product_id):
    """Supprimer un produit"""
    Product.delete(product_id)
    flash('Produit supprimé avec succès', 'success')
    return redirect(url_for('admin.products_list'))

# ========== GESTION COMMANDES ==========

@bp.route('/commandes')
@admin_required
def orders_list():
    """Liste des commandes"""
    status_filter = request.args.get('statut', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    skip = (page - 1) * per_page
    
    filters = {}
    if status_filter:
        filters['statut'] = status_filter
    
    orders = Order.get_all(filters=filters, limit=per_page, skip=skip)
    
    return render_template('admin/orders/list.html', orders=orders, current_status=status_filter, page=page)

@bp.route('/commandes/<order_id>')
@admin_required
def order_detail(order_id):
    """Détail d'une commande"""
    order = Order.get_by_id(order_id)
    if not order:
        flash('Commande introuvable', 'error')
        return redirect(url_for('admin.orders_list'))
    
    # Récupérer le client
    client = User.get_by_id(order['client_id'])
    
    return render_template('admin/orders/detail.html', order=order, client=client)

@bp.route('/commandes/<order_id>/statut', methods=['POST'])
@admin_required
def order_update_status(order_id):
    """Mettre à jour le statut d'une commande"""
    new_status = request.form.get('statut')
    if new_status:
        Order.update_status(order_id, new_status)
        flash('Statut de la commande mis à jour', 'success')
    return redirect(url_for('admin.order_detail', order_id=order_id))

# ========== GESTION UTILISATEURS ==========

@bp.route('/utilisateurs')
@admin_required
def users_list():
    """Liste des utilisateurs"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    skip = (page - 1) * per_page
    
    users = User.get_all(role='client', limit=per_page, skip=skip)
    
    return render_template('admin/users/list.html', users=users, page=page)

@bp.route('/utilisateurs/<user_id>/toggle', methods=['POST'])
@admin_required
def user_toggle(user_id):
    """Activer/désactiver un utilisateur"""
    user = User.get_by_id(user_id)
    if user:
        new_status = not user.get('actif', True)
        User.update(user_id, {'actif': new_status})
        status_text = 'activé' if new_status else 'désactivé'
        flash(f'Utilisateur {status_text}', 'success')
    return redirect(url_for('admin.users_list'))

# ========== GESTION CATÉGORIES ==========

@bp.route('/categories')
@admin_required
def categories_list():
    """Liste des catégories"""
    categories = Category.get_all()
    return render_template('admin/categories/list.html', categories=categories)

@bp.route('/categories/nouvelle', methods=['GET', 'POST'])
@admin_required
def category_add():
    """Ajouter une catégorie"""
    if request.method == 'POST':
        import re
        nom = request.form.get('nom', '').strip()
        slug = request.form.get('slug', '').strip() or re.sub(r'[^a-z0-9]+', '-', nom.lower())
        description = request.form.get('description', '').strip()
        
        data = {
            'nom': nom,
            'slug': slug,
            'description': description
        }
        
        Category.create(data)
        flash('Catégorie créée avec succès', 'success')
        return redirect(url_for('admin.categories_list'))
    
    return render_template('admin/categories/add.html')

@bp.route('/categories/<category_id>/edit', methods=['GET', 'POST'])
@admin_required
def category_edit(category_id):
    """Modifier une catégorie"""
    category = Category.get_by_id(category_id)
    if not category:
        flash('Catégorie introuvable', 'error')
        return redirect(url_for('admin.categories_list'))
    
    if request.method == 'POST':
        data = {
            'nom': request.form.get('nom', '').strip(),
            'slug': request.form.get('slug', '').strip(),
            'description': request.form.get('description', '').strip()
        }
        
        Category.update(category_id, data)
        flash('Catégorie mise à jour avec succès', 'success')
        return redirect(url_for('admin.categories_list'))
    
    return render_template('admin/categories/edit.html', category=category)

@bp.route('/categories/<category_id>/delete', methods=['POST'])
@admin_required
def category_delete(category_id):
    """Supprimer une catégorie"""
    Category.delete(category_id)
    flash('Catégorie supprimée avec succès', 'success')
    return redirect(url_for('admin.categories_list'))

