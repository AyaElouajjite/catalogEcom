# Guide de Démarrage Rapide

## Installation et Configuration

### 1. Prérequis
- Python 3.8 ou supérieur
- MongoDB Community Server installé et démarré
- pip (gestionnaire de paquets Python)

### 2. Installation

```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration MongoDB

Assurez-vous que MongoDB est démarré :

#### Windows

**Option 1 : Vérifier si MongoDB est déjà en cours d'exécution**
```powershell
# Vérifier si MongoDB écoute sur le port 27017
Test-NetConnection -ComputerName localhost -Port 27017
```

**Option 2 : Démarrer MongoDB comme service (si installé comme service)**
```powershell
# Lister les services MongoDB disponibles
Get-Service -Name "*mongo*"

# Si un service existe (ex: "MongoDB"), démarrer avec:
net start MongoDB
# ou avec PowerShell:
Start-Service MongoDB
```

**Option 3 : Démarrer MongoDB manuellement**
```powershell
# Trouver l'emplacement de MongoDB
# Généralement dans: C:\Program Files\MongoDB\Server\<version>\bin\

# Créer le répertoire de données si nécessaire
New-Item -ItemType Directory -Force -Path "$env:LOCALAPPDATA\MongoDB\data\db"

# Démarrer MongoDB manuellement (dans un nouveau terminal)
& "C:\Program Files\MongoDB\Server\<version>\bin\mongod.exe" --dbpath "$env:LOCALAPPDATA\MongoDB\data\db"
```

**Option 4 : Utiliser MongoDB Atlas (Cloud - Recommandé pour débuter)**
1. Créer un compte gratuit sur https://www.mongodb.com/cloud/atlas
2. Créer un cluster gratuit
3. Obtenir la chaîne de connexion
4. Modifier `.env` avec votre URI MongoDB Atlas :
   ```
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
   ```

#### Linux/Mac
```bash
sudo systemctl start mongod
# ou
mongod
```

### 4. Configuration de l'application

Créez un fichier `.env` à partir de `env.example` :
```bash
# Windows
copy env.example .env

# Linux/Mac
cp env.example .env
```

Modifiez `.env` si nécessaire (par défaut, MongoDB sur localhost:27017).

### 5. Initialisation de la base de données

```bash
python init_db.py
```

Cela va :
- Créer les collections nécessaires
- Créer les index
- Créer un compte administrateur par défaut :
  - Email: `admin@example.com`
  - Mot de passe: `admin123`

### 6. Lancer l'application

```bash
python app.py
```

L'application sera accessible sur `http://localhost:5000`

## Utilisation

### Frontend Public
- Accueil: `http://localhost:5000/`
- Catalogue: `http://localhost:5000/catalogue`
- Connexion: `http://localhost:5000/login`
- Inscription: `http://localhost:5000/register`

### Backend Admin
- Dashboard: `http://localhost:5000/admin`
- Connexion avec: `admin@example.com` / `admin123`

## Structure des Données

### Créer un produit avec attributs variables

1. Aller dans Admin > Produits > Nouveau produit
2. Remplir les informations de base
3. Dans "Attributs variables", ajouter:
   - Nom: `Taille`, Valeurs: `S, M, L, XL`
   - Nom: `Couleur`, Valeurs: `Rouge, Bleu, Noir`
4. Le système génère automatiquement toutes les combinaisons (S-Rouge, S-Bleu, etc.)
5. Après création, éditer le produit pour définir prix et stock par variation

## Dépannage

### MongoDB ne démarre pas

**Erreur "The service name is invalid" sur Windows :**
- MongoDB n'est probablement pas installé comme service Windows
- Solutions :
  1. **Démarrer manuellement** : Trouvez `mongod.exe` dans `C:\Program Files\MongoDB\Server\<version>\bin\` et exécutez-le
  2. **Installer comme service** : Réinstallez MongoDB avec l'option "Install MongoDB as a Service"
  3. **Utiliser MongoDB Atlas** : Utilisez MongoDB cloud (gratuit) au lieu d'une installation locale

**Autres problèmes :**
- Vérifiez que le port 27017 n'est pas utilisé : `Test-NetConnection -ComputerName localhost -Port 27017`
- Vérifiez les permissions d'écriture dans le répertoire de données MongoDB
- Créez le répertoire de données : `New-Item -ItemType Directory -Force -Path "$env:LOCALAPPDATA\MongoDB\data\db"`

### Erreur de connexion MongoDB
- Vérifiez que MongoDB est démarré : `Test-NetConnection -ComputerName localhost -Port 27017`
- Vérifiez l'URI dans `.env` (par défaut: `mongodb://localhost:27017/`)
- Si vous utilisez MongoDB Atlas, vérifiez que votre IP est autorisée dans les paramètres réseau

### Erreur d'import
- Assurez-vous d'être dans le répertoire du projet
- Vérifiez que l'environnement virtuel est activé
- Réinstallez les dépendances: `pip install -r requirements.txt`

## Notes Importantes

- **Sécurité**: Changez le mot de passe admin en production !
- **Images**: Les images uploadées sont stockées dans `static/images/uploads/`
- **Sessions**: Les sessions Flask sont stockées côté serveur (par défaut en mémoire)
- **Production**: Configurez `SECRET_KEY` avec une valeur sécurisée aléatoire


