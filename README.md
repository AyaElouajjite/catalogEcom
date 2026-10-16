# 🛍️ CatalogEcom — Catalogue e-commerce avec Flask et MongoDB

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?logo=mongodb&logoColor=white)

Application web **full-stack** d'e-commerce : une boutique publique pour les clients et un back-office complet pour gérer le catalogue, les commandes et les utilisateurs. Les données sont stockées dans une base **NoSQL MongoDB**.

---

## ✨ Fonctionnalités

### 🛒 Boutique publique
- Catalogue de produits avec **filtres**
- Fiche produit avec **attributs variables** (taille, couleur…)
- **Panier** d'achat
- Processus de **commande** et de **paiement**
- **Espace client** : compte et historique des commandes

### 🧑‍💼 Back-office administrateur
- **Tableau de bord** avec statistiques
- Gestion des **produits** et des **catégories** (CRUD, upload d'images)
- Gestion des **commandes**
- Gestion des **utilisateurs**

### 🔐 Sécurité
- Inscription et connexion
- Mots de passe chiffrés avec **bcrypt**

## 🛠️ Technologies

| Couche | Outils |
|---|---|
| Backend | Python, Flask, Jinja2 |
| Base de données | MongoDB (PyMongo) |
| Frontend | HTML, CSS, JavaScript |
| Autres | bcrypt, python-dotenv, Pillow |

## 🏗️ Architecture

```
catalogEcom/
├── app.py            # Point d'entrée Flask
├── init_db.py        # Initialisation de la base
├── src/
│   ├── models/       # Modèles MongoDB (product, category, order, user)
│   ├── routes/       # Routes : public, auth, cart, admin
│   └── utils/        # Authentification
├── templates/        # Vues : public, auth, admin
└── static/           # CSS, JS, images
```

## 🚀 Installation

**Prérequis :** Python 3.8+, MongoDB Community Server

```bash
git clone https://github.com/AyaElouajjite/catalogEcom.git
cd catalogEcom

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / macOS

pip install -r requirements.txt
cp env.example .env          # adapter la configuration si nécessaire

python init_db.py
python app.py
```

L'application est disponible sur **http://localhost:5000**.

Guides complémentaires : [`QUICKSTART.md`](QUICKSTART.md), [`INSTALL_MONGODB.md`](INSTALL_MONGODB.md), [`MONGODB_TROUBLESHOOTING.md`](MONGODB_TROUBLESHOOTING.md).

## 🔐 Compte administrateur par défaut

| E-mail | Mot de passe |
|---|---|
| `admin@example.com` | `admin123` |

> ⚠️ Pensez à modifier ce mot de passe en production.

## 👩‍💻 Auteur

**Aya Elouajjite** — [@AyaElouajjite](https://github.com/AyaElouajjite)
