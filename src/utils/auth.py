"""
Utilitaires d'authentification
"""
import bcrypt
from functools import wraps
from flask import session, redirect, url_for, request
from src.models.database import get_db

def hash_password(password):
    """Hash un mot de passe avec bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, password_hash):
    """Vérifie un mot de passe contre son hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def login_required(f):
    """Décorateur pour protéger les routes nécessitant une authentification"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Décorateur pour protéger les routes admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login', next=request.url))
        
        db = get_db()
        # L'ID est stocké en string dans la session, il faut le reconvertir en ObjectId
        from bson import ObjectId
        try:
            user_id = ObjectId(session['user_id'])
        except Exception:
            session.clear()
            return redirect(url_for('auth.login', next=request.url))

        user = db.users.find_one({"_id": user_id})
        if not user or user.get('role') != 'admin':
            return redirect(url_for('public.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Récupère l'utilisateur actuellement connecté"""
    if 'user_id' not in session:
        return None
    
    db = get_db()
    from bson import ObjectId
    user = db.users.find_one({"_id": ObjectId(session['user_id'])})
    if user:
        user['_id'] = str(user['_id'])
    return user

