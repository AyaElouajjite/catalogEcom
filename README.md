# E-Commerce Product Catalog Web

Application web full-stack de gestion e-commerce développée avec Python (Flask) et MongoDB.

## 🚀 Installation

### Prérequis

- Python 3.8+
- MongoDB Community Server
- Navigateur web moderne

### Étapes d'installation

1. **Cloner le projet**
```bash
git clone <repository-url>
cd nosqleco
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer MongoDB**
- Démarrer MongoDB Community Server
- Créer un fichier `.env` à partir de `.env.example`
- Modifier les variables d'environnement si nécessaire

5. **Initialiser la base de données**
```bash
python init_db.py
```

6. **Lancer l'application**
```bash
python app.py
```

L'application sera accessible sur `http://localhost:5000`

## 📁 Structure du Projet

```
ecommerce-web/
├── app.py                 # Application principale Flask
├── requirements.txt       # Dépendances Python
├── .env                  # Variables d'environnement
├── init_db.py           # Script d'initialisation BDD
│
├── static/              # Fichiers statiques
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/           # Templates Jinja2
│   ├── public/
│   ├── auth/
│   └── admin/
│
└── src/                 # Code source
    ├── models/          # Modèles MongoDB
    ├── routes/          # Routes Flask
    ├── forms/           # Formulaires
    ├── utils/           # Utilitaires
    └── services/        # Services métier
```

## 🔐 Comptes par défaut

Après l'initialisation, un compte administrateur est créé :
- Email: admin@example.com
- Mot de passe: admin123

**⚠️ Important : Changez ce mot de passe en production !**

## 🛠️ Fonctionnalités

### Frontend Public
- Catalogue produits avec filtres
- Détail produit avec attributs variables
- Panier d'achat
- Processus de commande
- Espace client

### Backend Admin
- Dashboard avec statistiques
- Gestion produits (CRUD)
- Gestion attributs variables
- Gestion commandes
- Gestion utilisateurs

## 📝 Notes

- Les images uploadées sont stockées dans `static/images/uploads/`
- MongoDB doit être démarré avant de lancer l'application
- En développement, le mode debug est activé


