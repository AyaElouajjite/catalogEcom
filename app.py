"""
Application principale Flask - E-Commerce
"""
import os
from flask import Flask, render_template, session
from dotenv import load_dotenv
from src.routes import public, auth, admin, cart
from src.utils.auth import get_current_user

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration
app.config['UPLOAD_FOLDER'] = 'static/images/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enregistrer les blueprints
app.register_blueprint(public.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(cart.bp)

# Context processor pour rendre l'utilisateur disponible dans tous les templates
@app.context_processor
def inject_user():
    return dict(current_user=get_current_user())

# Gestion des erreurs
@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    # Créer le dossier uploads s'il n'existe pas
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=os.getenv('FLASK_DEBUG', 'True') == 'True', host='0.0.0.0', port=5000)


