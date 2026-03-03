"""
Routes pour le panier d'achat
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from src.utils.auth import login_required
from src.models.product import Product
from src.models.order import Order
from bson import ObjectId

bp = Blueprint('cart', __name__, url_prefix='/')

def get_cart():
    """Récupère le panier depuis la session"""
    return session.get('cart', [])

def save_cart(cart):
    """Sauvegarde le panier dans la session"""
    session['cart'] = cart

@bp.route('/panier')
def cart():
    """Page panier"""
    cart_items = get_cart()
    cart_with_details = []
    total = 0
    
    for item in cart_items:
        product = Product.get_by_id(item['product_id'])
        if product:
            variation = None
            if item.get('variation_id'):
                variation = Product.get_variation(item['product_id'], item['variation_id'])
            
            price = variation.get('prix') if variation else product.get('prix_base', 0)
            quantity = item.get('quantity', 1)
            item_total = price * quantity
            total += item_total
            
            cart_with_details.append({
                'product': product,
                'variation': variation,
                'quantity': quantity,
                'price': price,
                'total': item_total
            })
    
    return render_template('public/cart.html', cart_items=cart_with_details, total=total)

@bp.route('/panier/ajouter', methods=['POST'])
@login_required
def add_to_cart():
    """Ajoute un produit au panier"""
    product_id = request.form.get('product_id')
    variation_id = request.form.get('variation_id', '').strip() or None
    quantity = int(request.form.get('quantity', 1))
    
    if not product_id:
        flash('Produit introuvable', 'error')
        return redirect(url_for('public.catalogue'))
    
    product = Product.get_by_id(product_id)
    if not product or not product.get('publie'):
        flash('Produit introuvable', 'error')
        return redirect(url_for('public.catalogue'))
    
    # Vérifier le stock si variation
    if variation_id:
        variation = Product.get_variation(product_id, variation_id)
        if not variation or variation.get('stock', 0) < quantity:
            flash('Stock insuffisant', 'error')
            return redirect(url_for('public.product_detail', product_id=product_id))
    
    cart = get_cart()
    
    # Vérifier si le produit existe déjà dans le panier
    found = False
    for item in cart:
        if item['product_id'] == product_id and (item.get('variation_id') or None) == variation_id:
            item['quantity'] += quantity
            found = True
            break
    
    if not found:
        cart.append({
            'product_id': product_id,
            'variation_id': variation_id,
            'quantity': quantity
        })
    
    save_cart(cart)
    flash('Produit ajouté au panier', 'success')
    
    if request.headers.get('Content-Type') == 'application/json':
        return jsonify({'success': True, 'cart_count': len(cart)})
    
    return redirect(request.referrer or url_for('public.catalogue'))

@bp.route('/panier/modifier', methods=['POST'])
@login_required
def update_cart():
    """Modifie la quantité d'un article dans le panier"""
    product_id = request.form.get('product_id')
    variation_id = request.form.get('variation_id', '').strip() or None
    quantity = int(request.form.get('quantity', 1))
    
    cart = get_cart()
    
    for item in cart:
        if item['product_id'] == product_id and (item.get('variation_id') or None) == variation_id:
            if quantity <= 0:
                cart.remove(item)
            else:
                item['quantity'] = quantity
            break
    
    save_cart(cart)
    flash('Panier mis à jour', 'success')
    return redirect(url_for('cart.cart'))

@bp.route('/panier/supprimer', methods=['POST'])
@login_required
def remove_from_cart():
    """Supprime un article du panier"""
    product_id = request.form.get('product_id')
    variation_id = request.form.get('variation_id', '').strip() or None
    
    cart = get_cart()
    cart = [item for item in cart if not (
        item['product_id'] == product_id and (item.get('variation_id') or None) == variation_id
    )]
    
    save_cart(cart)
    flash('Article supprimé du panier', 'success')
    return redirect(url_for('cart.cart'))

@bp.route('/commander', methods=['GET', 'POST'])
@login_required
def checkout():
    """Processus de commande"""
    from src.utils.auth import get_current_user
    
    cart_items = get_cart()
    if not cart_items:
        flash('Votre panier est vide', 'error')
        return redirect(url_for('cart.cart'))
    
    user = get_current_user()
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        adresse_livraison = {
            'nom': request.form.get('nom', user.get('nom', '')),
            'prenom': request.form.get('prenom', user.get('prenom', '')),
            'rue': request.form.get('rue', ''),
            'ville': request.form.get('ville', ''),
            'code_postal': request.form.get('code_postal', ''),
            'pays': request.form.get('pays', 'France'),
            'telephone': request.form.get('telephone', user.get('telephone', ''))
        }
        
        mode_paiement = request.form.get('mode_paiement', 'carte')
        
        # Validation
        required_fields = ['nom', 'prenom', 'rue', 'ville', 'code_postal']
        if not all(adresse_livraison.get(field) for field in required_fields):
            flash('Veuillez remplir tous les champs obligatoires', 'error')
            return render_template('public/checkout.html', user=user, cart_items=cart_items, total=total)
        
        # Si carte bancaire ou PayPal, rediriger vers la page de paiement
        if mode_paiement in ['carte', 'paypal']:
            # Sauvegarder les données dans la session pour la page de paiement
            session['checkout_data'] = {
                'adresse_livraison': adresse_livraison,
                'mode_paiement': mode_paiement
            }
            return redirect(url_for('cart.payment'))
        
        # Pour virement bancaire, continuer avec le processus normal
        
        # Construire les articles de la commande + vérification stock + décrément
        articles = []
        sous_total = 0
        product_updates = []
        
        for item in cart_items:
            product = Product.get_by_id(item['product_id'])
            if not product:
                continue
            
            variation = None
            if item.get('variation_id'):
                variation = Product.get_variation(item['product_id'], item['variation_id'])
                if not variation:
                    flash('Une variation du produit est introuvable.', 'error')
                    return redirect(url_for('cart.cart'))
                # Vérifier stock variation
                if variation.get('stock', 0) < item.get('quantity', 1):
                    flash('Stock insuffisant pour une variation.', 'error')
                    return redirect(url_for('cart.cart'))
            else:
                # Pas de variation : si un champ stock existe dans le produit
                if product.get('stock') is not None and product.get('stock', 0) < item.get('quantity', 1):
                    flash('Stock insuffisant pour ce produit.', 'error')
                    return redirect(url_for('cart.cart'))
            
            price = variation.get('prix') if variation else product.get('prix_base', 0)
            quantity = item.get('quantity', 1)
            
            # Construire le nom avec les attributs de variation
            nom_produit = product['nom']
            if variation and variation.get('attributs'):
                attrs_str = ', '.join([f"{k}: {v}" for k, v in variation['attributs'].items()])
                nom_produit = f"{nom_produit} ({attrs_str})"
            
            # Récupérer l'image du produit
            image_produit = None
            if product.get('images_principales') and len(product['images_principales']) > 0:
                image_produit = product['images_principales'][0]
            elif variation and variation.get('images') and len(variation['images']) > 0:
                image_produit = variation['images'][0]
            
            articles.append({
                'produit_id': ObjectId(item['product_id']),
                'variation_id': ObjectId(item['variation_id']) if item.get('variation_id') else None,
                'nom': nom_produit,
                'quantite': quantity,
                'prix_unitaire': price,
                'image': image_produit
            })
            
            sous_total += price * quantity
            
            # Préparer décrément stock
            if variation:
                product_updates.append({
                    'product_id': item['product_id'],
                    'variation_id': item['variation_id'],
                    'delta': -quantity
                })
            elif product.get('stock') is not None:
                product_updates.append({
                    'product_id': item['product_id'],
                    'variation_id': None,
                    'delta': -quantity
                })
        
        frais_livraison = 4.99  # Fixe pour l'exemple
        total = sous_total + frais_livraison
        
        # Créer la commande
        order_data = {
            'client_id': ObjectId(user['_id']),
            'articles': articles,
            'sous_total': sous_total,
            'frais_livraison': frais_livraison,
            'total': total,
            'adresse_livraison': adresse_livraison,
            'statut': 'en_attente',
            'mode_paiement': request.form.get('mode_paiement', 'carte')
        }
        
        order_id = Order.create(order_data)
        
        # Appliquer décrément de stock (variations ou produit)
        for upd in product_updates:
            Product.decrement_stock(
                product_id=upd['product_id'],
                variation_id=upd['variation_id'],
                delta=upd['delta']
            )
        
        # Vider le panier
        save_cart([])
        
        flash('Commande passée avec succès!', 'success')
        return redirect(url_for('cart.order_confirmation', order_id=str(order_id)))
    
    # Calculer le total pour l'affichage
    total = 0
    for item in cart_items:
        product = Product.get_by_id(item['product_id'])
        if product:
            variation = None
            if item.get('variation_id'):
                variation = Product.get_variation(item['product_id'], item['variation_id'])
            price = variation.get('prix') if variation else product.get('prix_base', 0)
            total += price * item.get('quantity', 1)
    
    return render_template('public/checkout.html', user=user, cart_items=cart_items, total=total)

@bp.route('/paiement', methods=['GET', 'POST'])
@login_required
def payment():
    """Page de finalisation du paiement"""
    from src.utils.auth import get_current_user
    
    cart_items = get_cart()
    if not cart_items:
        flash('Votre panier est vide', 'error')
        return redirect(url_for('cart.cart'))
    
    # Récupérer les données de checkout depuis la session
    checkout_data = session.get('checkout_data')
    if not checkout_data:
        flash('Veuillez d\'abord remplir les informations de livraison', 'error')
        return redirect(url_for('cart.checkout'))
    
    user = get_current_user()
    mode_paiement = checkout_data.get('mode_paiement', 'carte')
    
    # Calculer le total
    total = 0
    for item in cart_items:
        product = Product.get_by_id(item['product_id'])
        if product:
            variation = None
            if item.get('variation_id'):
                variation = Product.get_variation(item['product_id'], item['variation_id'])
            price = variation.get('prix') if variation else product.get('prix_base', 0)
            total += price * item.get('quantity', 1)
    
    frais_livraison = 4.99
    total_final = total + frais_livraison
    
    if request.method == 'POST':
        # Traiter le paiement
        if mode_paiement == 'carte':
            # Validation des données de carte
            numero_carte = request.form.get('numero_carte', '').replace(' ', '').replace('-', '')
            date_expiration = request.form.get('date_expiration', '')
            cvv = request.form.get('cvv', '')
            nom_titulaire = request.form.get('nom_titulaire', '')
            
            if not all([numero_carte, date_expiration, cvv, nom_titulaire]):
                flash('Veuillez remplir tous les champs de la carte bancaire', 'error')
                return render_template('public/payment.html', 
                                     checkout_data=checkout_data, 
                                     total=total, 
                                     total_final=total_final,
                                     mode_paiement=mode_paiement)
            
            # Ici, normalement, on ferait appel à une API de paiement
            # Pour l'instant, on simule juste le paiement
            
        elif mode_paiement == 'paypal':
            email_paypal = request.form.get('email_paypal', '')
            if not email_paypal:
                flash('Veuillez entrer votre email PayPal', 'error')
                return render_template('public/payment.html', 
                                     checkout_data=checkout_data, 
                                     total=total, 
                                     total_final=total_final,
                                     mode_paiement=mode_paiement)
        
        # Créer la commande
        adresse_livraison = checkout_data['adresse_livraison']
        articles = []
        sous_total = 0
        product_updates = []
        
        for item in cart_items:
            product = Product.get_by_id(item['product_id'])
            if not product:
                continue
            
            variation = None
            if item.get('variation_id'):
                variation = Product.get_variation(item['product_id'], item['variation_id'])
                if not variation:
                    flash('Une variation du produit est introuvable.', 'error')
                    return redirect(url_for('cart.cart'))
                if variation.get('stock', 0) < item.get('quantity', 1):
                    flash('Stock insuffisant pour une variation.', 'error')
                    return redirect(url_for('cart.cart'))
            else:
                if product.get('stock') is not None and product.get('stock', 0) < item.get('quantity', 1):
                    flash('Stock insuffisant pour ce produit.', 'error')
                    return redirect(url_for('cart.cart'))
            
            price = variation.get('prix') if variation else product.get('prix_base', 0)
            quantity = item.get('quantity', 1)
            
            nom_produit = product['nom']
            if variation and variation.get('attributs'):
                attrs_str = ', '.join([f"{k}: {v}" for k, v in variation['attributs'].items()])
                nom_produit = f"{nom_produit} ({attrs_str})"
            
            image_produit = None
            if product.get('images_principales') and len(product['images_principales']) > 0:
                image_produit = product['images_principales'][0]
            elif variation and variation.get('images') and len(variation['images']) > 0:
                image_produit = variation['images'][0]
            
            articles.append({
                'produit_id': ObjectId(item['product_id']),
                'variation_id': ObjectId(item['variation_id']) if item.get('variation_id') else None,
                'nom': nom_produit,
                'quantite': quantity,
                'prix_unitaire': price,
                'image': image_produit
            })
            
            sous_total += price * quantity
            
            if variation:
                product_updates.append({
                    'product_id': item['product_id'],
                    'variation_id': item['variation_id'],
                    'delta': -quantity
                })
            elif product.get('stock') is not None:
                product_updates.append({
                    'product_id': item['product_id'],
                    'variation_id': None,
                    'delta': -quantity
                })
        
        order_data = {
            'client_id': ObjectId(user['_id']),
            'articles': articles,
            'sous_total': sous_total,
            'frais_livraison': frais_livraison,
            'total': total_final,
            'adresse_livraison': adresse_livraison,
            'statut': 'payee' if mode_paiement in ['carte', 'paypal'] else 'en_attente',
            'mode_paiement': mode_paiement
        }
        
        order_id = Order.create(order_data)
        
        # Appliquer décrément de stock
        for upd in product_updates:
            Product.decrement_stock(
                product_id=upd['product_id'],
                variation_id=upd['variation_id'],
                delta=upd['delta']
            )
        
        # Vider le panier et les données de checkout
        save_cart([])
        session.pop('checkout_data', None)
        
        flash('Commande passée avec succès!', 'success')
        return redirect(url_for('cart.order_confirmation', order_id=str(order_id)))
    
    return render_template('public/payment.html', 
                         checkout_data=checkout_data, 
                         total=total, 
                         total_final=total_final,
                         mode_paiement=mode_paiement)

@bp.route('/commande/confirmation/<order_id>')
@login_required
def order_confirmation(order_id):
    """Page de confirmation de commande"""
    from src.utils.auth import get_current_user
    from src.models.order import Order
    
    user = get_current_user()
    order = Order.get_by_id(order_id)
    
    if not order or str(order['client_id']) != user['_id']:
        flash('Commande introuvable', 'error')
        return redirect(url_for('public.index'))
    
    return render_template('public/order_confirmation.html', order=order)

