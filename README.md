# CatalogEcom — Plateforme e-commerce avec Flask et MongoDB

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?logo=mongodb&logoColor=white)

Application web e-commerce full-stack comprenant une boutique en ligne pour les clients et un back-office pour l'administration du catalogue, des commandes et des utilisateurs. Les données sont stockées dans une base NoSQL MongoDB.

## Fonctionnalités

**Boutique en ligne**
- Catalogue de produits avec filtres
- Fiches produits avec attributs variables (taille, couleur, etc.)
- Panier, commande et paiement
- Espace client avec historique des commandes

**Back-office**
- Tableau de bord avec indicateurs
- Gestion des produits et des catégories, avec téléversement d'images
- Gestion des commandes
- Gestion des utilisateurs

## Points techniques

- Application Flask organisée en **Blueprints** (public, authentification, panier, administration)
- Modélisation de documents MongoDB adaptée aux attributs variables des produits
- Hachage des mots de passe avec **bcrypt** et contrôle d'accès à l'espace d'administration
- Configuration externalisée par variables d'environnement (`python-dotenv`)
- Script d'initialisation de la base de données
- Pages d'erreur personnalisées (404, 500)

## Stack technique

| Domaine | Technologies |
|---|---|
| Backend | Python, Flask, Jinja2 |
| Base de données | MongoDB, PyMongo |
| Frontend | HTML, CSS, JavaScript |
| Sécurité et outils | bcrypt, python-dotenv, Pillow |

## Architecture

```
catalogEcom/
├── app.py            # Point d'entrée
├── init_db.py        # Initialisation de la base
├── src/
│   ├── models/       # Produits, catégories, commandes, utilisateurs
│   ├── routes/       # Public, authentification, panier, administration
│   └── utils/        # Authentification
├── templates/        # Vues publiques, authentification, administration
└── static/           # CSS, JavaScript, images
```

## Installation

**Prérequis :** Python 3.8 ou supérieur, MongoDB Community Server.

```bash
git clone https://github.com/AyaElouajjite/catalogEcom.git
cd catalogEcom

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / macOS

pip install -r requirements.txt
cp env.example .env

python init_db.py
python app.py
```

L'application est accessible sur `http://localhost:5000`.

Documentation complémentaire : [QUICKSTART.md](QUICKSTART.md), [INSTALL_MONGODB.md](INSTALL_MONGODB.md), [MONGODB_TROUBLESHOOTING.md](MONGODB_TROUBLESHOOTING.md).

## Compte administrateur par défaut

| E-mail | Mot de passe |
|---|---|
| `admin@example.com` | `admin123` |

Ce mot de passe doit être modifié avant toute mise en production.

## Contact

**Aya Elouajjite** — [github.com/AyaElouajjite](https://github.com/AyaElouajjite)
