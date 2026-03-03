"""
Routes publiques (frontend client)
"""
from flask import Blueprint, render_template, request, jsonify
from src.models.product import Product
from src.models.category import Category
from src.models.order import Order
from src.utils.auth import login_required, get_current_user
from bson import ObjectId

bp = Blueprint('public', __name__)

@bp.route('/')
def index():
    """Page d'accueil"""
    # Produits phares (derniers produits publiés)
    featured_products = Product.get_all(
        filters={"publie": True},
        limit=8
    )
    return render_template('public/index.html', featured_products=featured_products)

@bp.route('/catalogue')
def catalogue():
    """Catalogue produits avec filtres"""
    category_slug = request.args.get('categorie', '')
    search_query = request.args.get('q', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Récupérer toutes les catégories
    categories = Category.get_all()
    
    # Construire les filtres
    filters = {"publie": True}
    
    if category_slug:
        category = Category.get_by_slug(category_slug)
        if category:
            filters['categorie_id'] = category['_id']
    
    # Recherche par texte
    products = []
    if search_query:
        products = Product.search(search_query, filters)
    else:
        products = Product.get_all(filters)
    
    # Filtrer par prix
    if min_price is not None or max_price is not None:
        filtered_products = []
        for product in products:
            price = product.get('prix_base', 0)
            if min_price is not None and price < min_price:
                continue
            if max_price is not None and price > max_price:
                continue
            filtered_products.append(product)
        products = filtered_products
    
    # Pagination
    total = len(products)
    start = (page - 1) * per_page
    end = start + per_page
    products_page = products[start:end]
    
    return render_template(
        'public/catalogue.html',
        products=products_page,
        categories=categories,
        current_category=category_slug,
        search_query=search_query,
        min_price=min_price,
        max_price=max_price,
        page=page,
        total_pages=(total + per_page - 1) // per_page,
        total=total
    )

@bp.route('/catalogue/<categorie>')
def catalogue_by_category(categorie):
    """Catalogue filtré par catégorie"""
    return catalogue()

@bp.route('/produit/<product_id>')
def product_detail(product_id):
    """Page détail produit"""
    product = Product.get_by_id(product_id)
    if not product or not product.get('publie'):
        return render_template('errors/404.html'), 404
    
    # Convertir les ObjectId en strings pour la sérialisation JSON
    if product.get('variations'):
        for variation in product['variations']:
            if '_id' in variation:
                variation['_id'] = str(variation['_id'])
    
    # Récupérer la catégorie
    category = None
    if product.get('categorie_id'):
        from src.models.category import Category
        category = Category.get_by_id(product['categorie_id'])
    
    # Produits similaires (même catégorie)
    similar_products = []
    if product.get('categorie_id'):
        similar_products = Product.get_all(
            filters={
                "categorie_id": product['categorie_id'],
                "publie": True,
                "_id": {"$ne": product_id}
            },
            limit=4
        )
    
    return render_template(
        'public/product.html',
        product=product,
        category=category,
        similar_products=similar_products
    )

@bp.route('/compte')
@login_required
def account():
    """Espace client - Profil"""
    return render_template('public/account.html')

@bp.route('/compte/modifier', methods=['POST'])
@login_required
def account_update():
    """Mise à jour du compte client"""
    from src.models.user import User
    from src.utils.auth import get_current_user, verify_password, hash_password
    
    user = get_current_user()
    
    # Récupérer les données du formulaire
    new_email = request.form.get('email', '').strip()
    new_telephone = request.form.get('telephone', '').strip()
    current_password = request.form.get('current_password', '').strip()
    new_password = request.form.get('new_password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()
    
    # Vérifier l'email
    if new_email and new_email != user.get('email'):
        # Vérifier si l'email existe déjà
        existing_user = User.get_by_email(new_email)
        if existing_user and str(existing_user['_id']) != user['_id']:
            flash('Cet email est déjà utilisé', 'error')
            return redirect(url_for('public.account'))
    
    # Mettre à jour les données
    update_data = {}
    
    if new_email:
        update_data['email'] = new_email
    
    if new_telephone:
        update_data['telephone'] = new_telephone
    
    # Gestion du mot de passe
    if new_password:
        if not current_password:
            flash('Veuillez entrer votre mot de passe actuel pour changer le mot de passe', 'error')
            return redirect(url_for('public.account'))
        
        # Vérifier le mot de passe actuel
        if not verify_password(current_password, user.get('password_hash', '')):
            flash('Mot de passe actuel incorrect', 'error')
            return redirect(url_for('public.account'))
        
        if new_password != confirm_password:
            flash('Les nouveaux mots de passe ne correspondent pas', 'error')
            return redirect(url_for('public.account'))
        
        if len(new_password) < 6:
            flash('Le mot de passe doit contenir au moins 6 caractères', 'error')
            return redirect(url_for('public.account'))
        
        # Hasher le nouveau mot de passe
        update_data['password_hash'] = hash_password(new_password)
    
    # Mettre à jour l'utilisateur
    if update_data:
        User.update(user['_id'], update_data)
        flash('Informations mises à jour avec succès', 'success')
    else:
        flash('Aucune modification à enregistrer', 'info')
    
    return redirect(url_for('public.account'))

@bp.route('/compte/commandes')
@login_required
def account_orders():
    """Espace client - Historique des commandes"""
    user = get_current_user()
    orders = Order.get_by_client(user['_id'])
    return render_template('public/account_orders.html', orders=orders)

@bp.route('/commande/<order_id>')
@login_required
def order_detail(order_id):
    """Détail d'une commande client"""
    user = get_current_user()
    order = Order.get_by_id(order_id)
    
    if not order or str(order['client_id']) != user['_id']:
        return render_template('errors/404.html'), 404
    
    return render_template('public/order_detail.html', order=order)

