"""
Routes d'authentification
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from src.models.user import User
from src.utils.auth import verify_password, hash_password, login_required

bp = Blueprint('auth', __name__, url_prefix='/')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Connexion utilisateur"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        next_url = request.args.get('next', url_for('public.index'))
        
        if not email or not password:
            flash('Veuillez remplir tous les champs', 'error')
            return render_template('auth/login.html')
        
        user = User.get_by_email(email)
        if not user:
            flash('Email ou mot de passe incorrect', 'error')
            return render_template('auth/login.html')
        
        if not user.get('actif', True):
            flash('Votre compte est désactivé', 'error')
            return render_template('auth/login.html')
        
        if not verify_password(password, user['password_hash']):
            flash('Email ou mot de passe incorrect', 'error')
            return render_template('auth/login.html')
        
        # Connexion réussie
        from bson import ObjectId
        session['user_id'] = str(user['_id'])
        session['user_email'] = user['email']
        session['user_role'] = user.get('role', 'client')
        
        flash('Connexion réussie!', 'success')
        
        # Rediriger selon le rôle
        if user.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(next_url)
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Inscription utilisateur"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        nom = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        telephone = request.form.get('telephone', '').strip()
        
        # Validation
        if not all([email, password, nom, prenom]):
            flash('Veuillez remplir tous les champs obligatoires', 'error')
            return render_template('auth/register.html')
        
        if password != password_confirm:
            flash('Les mots de passe ne correspondent pas', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Le mot de passe doit contenir au moins 6 caractères', 'error')
            return render_template('auth/register.html')
        
        # Vérifier si l'email existe déjà
        existing_user = User.get_by_email(email)
        if existing_user:
            flash('Cet email est déjà utilisé', 'error')
            return render_template('auth/register.html')
        
        # Créer l'utilisateur
        user_data = {
            'email': email,
            'password_hash': hash_password(password),
            'nom': nom,
            'prenom': prenom,
            'telephone': telephone,
            'role': 'client',
            'adresse': {},
            'actif': True
        }
        
        User.create(user_data)
        flash('Inscription réussie! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@bp.route('/logout')
@login_required
def logout():
    """Déconnexion utilisateur"""
    session.clear()
    flash('Déconnexion réussie', 'success')
    return redirect(url_for('public.index'))


