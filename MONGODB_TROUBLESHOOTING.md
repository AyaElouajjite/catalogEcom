# Guide de Dépannage MongoDB

## Problème : Le service MongoDB ne peut pas démarrer

### Solution 1 : Démarrer MongoDB manuellement (Recommandé)

Si le service Windows ne fonctionne pas, démarrez MongoDB manuellement :

1. **Trouver l'emplacement de MongoDB** :
```powershell
Get-ChildItem -Path "C:\Program Files\MongoDB\Server\*\bin\mongod.exe" -ErrorAction SilentlyContinue
```

2. **Créer le répertoire de données** :
```powershell
New-Item -ItemType Directory -Force -Path "$env:LOCALAPPDATA\MongoDB\data\db"
```

3. **Démarrer MongoDB manuellement** (dans un nouveau terminal PowerShell) :
```powershell
& "C:\Program Files\MongoDB\Server\<VERSION>\bin\mongod.exe" --dbpath "$env:LOCALAPPDATA\MongoDB\data\db"
```

Remplacez `<VERSION>` par votre version de MongoDB (ex: `7.0`, `6.0`, etc.)

### Solution 2 : Utiliser MongoDB Atlas (Cloud - Gratuit)

C'est la solution la plus simple si vous avez des problèmes avec l'installation locale :

1. **Créer un compte gratuit** sur https://www.mongodb.com/cloud/atlas
2. **Créer un cluster gratuit** (M0 Sandbox)
3. **Obtenir la chaîne de connexion** :
   - Cliquez sur "Connect" sur votre cluster
   - Choisissez "Connect your application"
   - Copiez la chaîne de connexion (format: `mongodb+srv://username:password@cluster.mongodb.net/`)

4. **Modifier le fichier `.env`** :
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
```

5. **Autoriser votre IP** dans MongoDB Atlas :
   - Allez dans "Network Access"
   - Ajoutez votre IP actuelle (ou `0.0.0.0/0` pour toutes les IPs - moins sécurisé)

### Solution 3 : Réinstaller MongoDB comme service

1. **Désinstaller MongoDB** complètement
2. **Télécharger MongoDB Community Server** depuis : https://www.mongodb.com/try/download/community
3. **Lors de l'installation**, cochez l'option "Install MongoDB as a Service"
4. **Redémarrer** votre ordinateur
5. **Vérifier** que le service fonctionne :
```powershell
Get-Service MongoDB
```

### Solution 4 : Démarrer MongoDB avec des privilèges administrateur

1. **Ouvrir PowerShell en tant qu'administrateur** (clic droit > Exécuter en tant qu'administrateur)
2. **Exécuter** :
```powershell
Start-Service MongoDB
```

### Vérifier que MongoDB fonctionne

Après avoir démarré MongoDB, vérifiez qu'il est accessible :

```powershell
Test-NetConnection -ComputerName localhost -Port 27017
```

Si la connexion réussit, vous verrez `TcpTestSucceeded : True`

## Commandes utiles

### Vérifier les services MongoDB
```powershell
Get-Service -Name "*mongo*"
```

### Arrêter MongoDB
```powershell
Stop-Service MongoDB
```

### Voir les processus MongoDB
```powershell
Get-Process mongod -ErrorAction SilentlyContinue
```

### Tuer un processus MongoDB bloqué
```powershell
Stop-Process -Name mongod -Force
```

