# Guide de Configuration MongoDB

## Problème : Erreur "The service name is invalid"

Cette erreur signifie que MongoDB n'est pas installé comme service Windows ou que le service n'existe pas.

## Solutions

### Solution 1 : Utiliser le script de démarrage automatique (Recommandé)

```powershell
.\start-mongodb.ps1
```

Ce script va :
- Vérifier si MongoDB est déjà en cours d'exécution
- Essayer de démarrer le service MongoDB s'il existe
- Démarrer MongoDB manuellement si nécessaire

### Solution 2 : Démarrer MongoDB manuellement

1. **Trouver l'emplacement de MongoDB** :
   ```powershell
   Get-ChildItem -Path "C:\Program Files\MongoDB" -Recurse -Filter "mongod.exe" -ErrorAction SilentlyContinue
   ```

2. **Créer le répertoire de données** :
   ```powershell
   New-Item -ItemType Directory -Force -Path "$env:LOCALAPPDATA\MongoDB\data\db"
   ```

3. **Démarrer MongoDB** (remplacez `<version>` par votre version) :
   ```powershell
   & "C:\Program Files\MongoDB\Server\<version>\bin\mongod.exe" --dbpath "$env:LOCALAPPDATA\MongoDB\data\db"
   ```

### Solution 3 : Utiliser MongoDB Atlas (Cloud - Gratuit)

1. Créez un compte sur https://www.mongodb.com/cloud/atlas
2. Créez un cluster gratuit (M0)
3. Obtenez votre chaîne de connexion
4. Modifiez le fichier `.env` :
   ```
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
   DATABASE_NAME=ecommerce_db
   ```

### Solution 4 : Réinstaller MongoDB comme service

1. Téléchargez MongoDB Community Server : https://www.mongodb.com/try/download/community
2. Pendant l'installation, cochez **"Install MongoDB as a Service"**
3. Après l'installation, MongoDB démarrera automatiquement

## Vérifier que MongoDB fonctionne

```powershell
# Vérifier si le port 27017 est ouvert
Test-NetConnection -ComputerName localhost -Port 27017

# Ou tester la connexion avec Python
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017/'); print('✓ Connexion réussie!')"
```

## Prochaines étapes

Une fois MongoDB démarré :

1. **Créer le fichier .env** (si pas déjà fait) :
   ```powershell
   copy env.example .env
   ```

2. **Initialiser la base de données** :
   ```powershell
   python init_db.py
   ```

3. **Lancer l'application** :
   ```powershell
   python app.py
   ```

## Dépannage supplémentaire

### Le port 27017 est déjà utilisé

```powershell
# Trouver quel processus utilise le port
netstat -ano | findstr :27017

# Arrêter le processus (remplacez PID par le numéro trouvé)
taskkill /PID <PID> /F
```

### Erreurs de permissions

Assurez-vous d'exécuter PowerShell en tant qu'administrateur si nécessaire.

### MongoDB ne démarre pas

Vérifiez les logs dans la fenêtre où vous avez lancé `mongod.exe` pour voir les erreurs spécifiques.


