# Guide d'Installation MongoDB sur Windows

## 📥 Lien de téléchargement

**MongoDB Community Server (Gratuit) :**
👉 https://www.mongodb.com/try/download/community

## 📋 Étapes d'installation

### Étape 1 : Téléchargement

1. Allez sur : https://www.mongodb.com/try/download/community
2. Sélectionnez :
   - **Version** : La dernière version stable (recommandé)
   - **Platform** : Windows
   - **Package** : MSI
3. Cliquez sur **Download**

### Étape 2 : Installation

1. **Lancez le fichier .msi téléchargé**

2. **Écran "Choose Setup Type"** :
   - Sélectionnez **"Complete"** (installation complète)
   - Cliquez sur **Next**

3. **Écran "Service Configuration"** ⚠️ **IMPORTANT** :
   - ✅ **COCHEZ** la case **"Install MongoDB as a Service"**
   - Sélectionnez **"Run service as Network Service user"** (par défaut)
   - Le nom du service sera **"MongoDB"**
   - Cliquez sur **Next**

4. **Écran "Install MongoDB Compass"** (optionnel) :
   - MongoDB Compass est une interface graphique
   - Vous pouvez le laisser coché si vous voulez une interface graphique
   - Cliquez sur **Next**

5. **Écran "Ready to install"** :
   - Vérifiez les options
   - Cliquez sur **Install**

6. **Attendez la fin de l'installation**

7. **Cliquez sur "Finish"**

### Étape 3 : Vérification

Après l'installation, MongoDB devrait démarrer automatiquement comme service.

**Vérifiez que le service est démarré :**

```powershell
# Vérifier le service MongoDB
Get-Service -Name "MongoDB"

# Si le service n'est pas démarré, démarrez-le :
Start-Service -Name "MongoDB"

# Ou avec la commande net :
net start MongoDB
```

**Vérifiez que MongoDB écoute sur le port 27017 :**

```powershell
Test-NetConnection -ComputerName localhost -Port 27017
```

## ✅ Après l'installation

Une fois MongoDB installé et démarré :

1. **Créez votre fichier .env** :
   ```powershell
   copy env.example .env
   ```

2. **Initialisez la base de données** :
   ```powershell
   python init_db.py
   ```

3. **Lancez l'application** :
   ```powershell
   python app.py
   ```

## 🔧 Si vous avez oublié de cocher "Install as a Service"

Si vous avez déjà installé MongoDB sans l'option service, vous pouvez :

### Option 1 : Réinstaller MongoDB
- Désinstallez MongoDB depuis le Panneau de configuration
- Réinstallez en suivant les étapes ci-dessus

### Option 2 : Installer manuellement comme service
```powershell
# Trouvez le chemin de mongod.exe (généralement) :
$mongodPath = "C:\Program Files\MongoDB\Server\<version>\bin\mongod.exe"

# Créez le répertoire de données
New-Item -ItemType Directory -Force -Path "C:\data\db"

# Installez comme service (en tant qu'administrateur)
& $mongodPath --install --serviceName "MongoDB" --serviceDisplayName "MongoDB" --dbpath "C:\data\db"

# Démarrez le service
Start-Service -Name "MongoDB"
```

## 📝 Notes importantes

- **Port par défaut** : MongoDB utilise le port **27017**
- **Répertoire de données** : Par défaut, MongoDB stocke les données dans `C:\data\db`
- **Service Windows** : Une fois installé comme service, MongoDB démarre automatiquement au démarrage de Windows
- **Arrêter MongoDB** : `net stop MongoDB` ou `Stop-Service -Name "MongoDB"`

## 🆘 Dépannage

### Le service ne démarre pas
- Vérifiez les logs dans : `C:\Program Files\MongoDB\Server\<version>\log\`
- Assurez-vous que le répertoire de données existe et a les bonnes permissions

### Le port 27017 est déjà utilisé
```powershell
# Trouver quel processus utilise le port
netstat -ano | findstr :27017
```

### Besoin d'aide ?
Consultez la documentation officielle : https://docs.mongodb.com/manual/installation/


