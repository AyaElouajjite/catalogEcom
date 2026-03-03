# Script pour démarrer MongoDB sur Windows
# Usage: .\start-mongodb.ps1

Write-Host "=== Vérification de MongoDB ===" -ForegroundColor Cyan

# Vérifier si MongoDB est déjà en cours d'exécution
$portTest = Test-NetConnection -ComputerName localhost -Port 27017 -InformationLevel Quiet -WarningAction SilentlyContinue
if ($portTest) {
    Write-Host "✓ MongoDB est déjà en cours d'exécution sur le port 27017" -ForegroundColor Green
    exit 0
}

Write-Host "MongoDB n'est pas en cours d'exécution. Tentative de démarrage..." -ForegroundColor Yellow

# Chercher le service MongoDB
$services = Get-Service -Name "*mongo*" -ErrorAction SilentlyContinue
if ($services) {
    Write-Host "Service MongoDB trouvé: $($services.Name)" -ForegroundColor Cyan
    foreach ($service in $services) {
        if ($service.Status -ne 'Running') {
            Write-Host "Démarrage du service $($service.Name)..." -ForegroundColor Yellow
            try {
                Start-Service -Name $service.Name
                Write-Host "✓ Service $($service.Name) démarré avec succès" -ForegroundColor Green
                Start-Sleep -Seconds 2
                $portTest = Test-NetConnection -ComputerName localhost -Port 27017 -InformationLevel Quiet -WarningAction SilentlyContinue
                if ($portTest) {
                    Write-Host "✓ MongoDB est maintenant accessible sur le port 27017" -ForegroundColor Green
                    exit 0
                }
            } catch {
                Write-Host "✗ Erreur lors du démarrage du service: $_" -ForegroundColor Red
                Write-Host "  Le service existe mais ne peut pas démarrer. Essayez de le démarrer manuellement avec des privilèges administrateur." -ForegroundColor Yellow
            }
        } else {
            Write-Host "✓ Service $($service.Name) est déjà en cours d'exécution" -ForegroundColor Green
        }
    }
}

# Chercher mongod.exe dans les emplacements communs
$mongodPaths = @(
    "C:\Program Files\MongoDB\Server\*\bin\mongod.exe",
    "C:\Program Files (x86)\MongoDB\Server\*\bin\mongod.exe",
    "$env:ProgramFiles\MongoDB\Server\*\bin\mongod.exe"
)

$mongodExe = $null
foreach ($path in $mongodPaths) {
    $found = Get-ChildItem -Path $path -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        $mongodExe = $found.FullName
        break
    }
}

if ($mongodExe) {
    Write-Host "MongoDB trouvé à: $mongodExe" -ForegroundColor Cyan
    
    # Créer le répertoire de données si nécessaire
    $dataPath = "$env:LOCALAPPDATA\MongoDB\data\db"
    if (-not (Test-Path $dataPath)) {
        Write-Host "Création du répertoire de données: $dataPath" -ForegroundColor Yellow
        New-Item -ItemType Directory -Force -Path $dataPath | Out-Null
    }
    
    Write-Host "Démarrage de MongoDB manuellement..." -ForegroundColor Yellow
    Write-Host "Note: MongoDB démarrera dans une nouvelle fenêtre. Gardez cette fenêtre ouverte." -ForegroundColor Cyan
    Write-Host ""
    
    # Démarrer MongoDB dans une nouvelle fenêtre
    Start-Process -FilePath $mongodExe -ArgumentList "--dbpath", "`"$dataPath`"" -WindowStyle Normal
    
    Write-Host "Attente du démarrage de MongoDB..." -ForegroundColor Yellow
    $maxAttempts = 10
    $attempt = 0
    while ($attempt -lt $maxAttempts) {
        Start-Sleep -Seconds 2
        $portTest = Test-NetConnection -ComputerName localhost -Port 27017 -InformationLevel Quiet -WarningAction SilentlyContinue
        if ($portTest) {
            Write-Host "✓ MongoDB est maintenant accessible sur le port 27017" -ForegroundColor Green
            exit 0
        }
        $attempt++
        Write-Host "  Tentative $attempt/$maxAttempts..." -ForegroundColor Gray
    }
    
    Write-Host "⚠ MongoDB a été lancé mais n'est pas encore accessible. Vérifiez la fenêtre MongoDB pour les erreurs." -ForegroundColor Yellow
} else {
    Write-Host "✗ MongoDB n'a pas été trouvé sur ce système." -ForegroundColor Red
    Write-Host ""
    Write-Host "Solutions possibles:" -ForegroundColor Yellow
    Write-Host "1. Installez MongoDB Community Server depuis: https://www.mongodb.com/try/download/community" -ForegroundColor White
    Write-Host "2. Ou utilisez MongoDB Atlas (cloud gratuit): https://www.mongodb.com/cloud/atlas" -ForegroundColor White
    Write-Host "3. Si MongoDB est installé ailleurs, modifiez ce script avec le bon chemin" -ForegroundColor White
    Write-Host ""
    Write-Host "Alternative: Utilisez MongoDB Atlas (gratuit) et modifiez votre fichier .env avec:" -ForegroundColor Cyan
    Write-Host "  MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/" -ForegroundColor White
    exit 1
}
