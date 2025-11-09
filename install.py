#!/usr/bin/env python3
"""
install.py - Script d'Installation BSV Wallet v4.0
==================================================

Ce script automatise l'installation complète du portefeuille modulaire.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header():
    """Affiche l'en-tête d'installation."""
    print("=" * 60)
    print("🚀 INSTALLATION BSV WALLET v4.0 MODULAIRE")
    print("=" * 60)
    print()

def check_python_version():
    """Vérifie la version de Python."""
    print("🐍 Vérification de Python...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ requis. Version actuelle:", sys.version)
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} détecté")
    return True

def create_directory_structure():
    """Crée la structure de dossiers."""
    print("\n📁 Création de la structure de dossiers...")
    
    directories = [
        "modules",
        "transactions", 
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   ✅ {directory}/")
    
    print("✅ Structure de dossiers créée")
    return True

def create_requirements_txt():
    """Crée le fichier requirements.txt."""
    print("\n📋 Création du fichier requirements.txt...")
    
    requirements = """# BSV Wallet v4.0 - Dépendances Python
bip-utils>=2.9.0
base58>=2.1.1
ecdsa>=0.18.0
configparser>=5.3.0
"""
    
    try:
        with open("requirements.txt", "w") as f:
            f.write(requirements)
        print("✅ requirements.txt créé")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création de requirements.txt: {e}")
        return False

def setup_virtual_environment():
    """Configure l'environnement virtuel."""
    print("\n🔧 Configuration de l'environnement virtuel...")
    
    try:
        # Créer l'environnement virtuel
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Environnement virtuel créé")
        
        # Déterminer la commande d'activation selon l'OS
        if os.name == 'nt':  # Windows
            pip_cmd = "venv\\Scripts\\pip"
            activate_cmd = "venv\\Scripts\\activate"
        else:  # Linux/Mac
            pip_cmd = "venv/bin/pip"
            activate_cmd = "source venv/bin/activate"
        
        # Installer les dépendances
        print("📦 Installation des dépendances...")
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dépendances installées")
        
        print(f"\n💡 Pour activer l'environnement virtuel:")
        print(f"   {activate_cmd}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la configuration: {e}")
        return False

def create_example_config():
    """Crée un fichier config.ini d'exemple."""
    print("\n⚙️ Création du fichier config.ini...")
    
    config_content = """[Credentials]
# Votre phrase mnémonique BIP39 (12 mots)
# IMPORTANT: Gardez cette phrase secrète et sécurisée!
# Remplacez la ligne ci-dessous par votre vraie mnémonique de 12 mots
mnemonic = your twelve word mnemonic phrase goes here exactly as given

# Passcode BIP39 optionnel (laisser vide si aucun)
passcode = 

[Transaction]
# Adresse de destination pour les envois
destination_address = 1DestinationAddressGoesHere

# Montant à envoyer en BSV (ex: 0.001)
amount_to_send_bsv = 0.001

# Frais par byte en satoshis (recommandé: 1-2)
fee_per_byte = 1

[SPV]
# Intervalle de vérification en secondes pour le mode SPV
check_interval = 3

# Afficher les vérifications périodiques (true/false)
show_periodic_checks = true
"""
    
    try:
        with open("config.ini", "w") as f:
            f.write(config_content)
        print("✅ config.ini créé")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création de config.ini: {e}")
        return False

def create_readme():
    """Crée un fichier README."""
    print("\n📖 Création du README...")
    
    readme_content = """# BSV Wallet v4.0 - Modulaire

## Installation Terminée ✅

Votre portefeuille BSV modulaire est maintenant installé !

## Structure du Projet

```
BSV_Wallet_v4/
├── main.py                    # Point d'entrée principal
├── config.ini                 # Configuration (⚠️ À CONFIGURER)
├── requirements.txt           # Dépendances Python
├── modules/                   # Modules Python
│   ├── wallet_config.py       # Gestion configuration
│   ├── wallet_crypto.py       # Cryptographie
│   ├── wallet_network.py      # Communication réseau
│   ├── wallet_transaction.py  # Transactions
│   ├── wallet_scanner.py      # Scanner d'adresses
│   └── wallet_ui.py           # Interface utilisateur
├── venv/                      # Environnement virtuel Python
├── transactions/              # Transactions sauvegardées
└── logs/                      # Logs du programme
```

## 🚀 Démarrage Rapide

### 1. Configurer votre mnémonique
Éditez `config.ini` et remplacez :
```ini
mnemonic = your twelve word mnemonic phrase goes here exactly as given
```
Par votre vraie mnémonique de 12 mots.

### 2. Activer l'environnement virtuel
```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\\Scripts\\activate
```

### 3. Lancer le portefeuille
```bash
python main.py
```

## 🔧 Fonctionnalités

- ✅ **Portefeuille multi-adresses** - Combine automatiquement les UTXOs
- ✅ **Mode SPV** - Surveillance temps réel des transactions
- ✅ **Interface interactive** - Menu facile à utiliser
- ✅ **Architecture modulaire** - Code organisé et maintenable
- ✅ **Signatures BSV** - Support complet Bitcoin SV

## ⚠️ Sécurité

- **Gardez votre mnémonique secrète**
- **Sauvegardez votre config.ini** (sans la mnémonique en ligne)
- **Testez avec de petits montants** d'abord
- **Utilisez un système sécurisé**

## 📞 Support

Consultez `STRUCTURE_PROJET.md` pour les détails techniques et l'évolution du code.

---
BSV Wallet v4.0 - Architecture Modulaire 🚀
"""
    
    try:
        with open("README.md", "w") as f:
            f.write(readme_content)
        print("✅ README.md créé")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création du README: {e}")
        return False

def create_launcher_script():
    """Crée un script de lancement."""
    print("\n🚀 Création du script de lancement...")
    
    if os.name == 'nt':  # Windows
        launcher_content = """@echo off
echo Activation de l'environnement virtuel...
call venv\\Scripts\\activate
echo Lancement du BSV Wallet v4.0...
python main.py
pause
"""
        filename = "launch_wallet.bat"
    else:  # Linux/Mac
        launcher_content = """#!/bin/bash
echo "Activation de l'environnement virtuel..."
source venv/bin/activate
echo "Lancement du BSV Wallet v4.0..."
python3 main.py
"""
        filename = "launch_wallet.sh"
    
    try:
        with open(filename, "w") as f:
            f.write(launcher_content)
        
        # Rendre exécutable sur Linux/Mac
        if os.name != 'nt':
            os.chmod(filename, 0o755)
        
        print(f"✅ {filename} créé")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création du launcher: {e}")
        return False

def print_final_instructions():
    """Affiche les instructions finales."""
    print("\n" + "=" * 60)
    print("🎉 INSTALLATION TERMINÉE AVEC SUCCÈS !")
    print("=" * 60)
    print()
    print("📝 ÉTAPES SUIVANTES:")
    print("1. ⚙️  Configurez votre mnémonique dans config.ini")
    print("2. 🔄 Activez l'environnement virtuel:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("3. 🚀 Lancez le portefeuille:")
    print("   python main.py")
    print()
    print("💡 OU utilisez le script de lancement:")
    if os.name == 'nt':
        print("   Double-cliquez sur launch_wallet.bat")
    else:
        print("   ./launch_wallet.sh")
    print()
    print("📖 Consultez README.md pour plus d'informations")
    print("🏗️  Consultez STRUCTURE_PROJET.md pour les détails techniques")
    print()
    print("⚠️  N'OUBLIEZ PAS de configurer votre mnémonique de 12 mots !")
    print("=" * 60)

def main():
    """Fonction principale d'installation."""
    print_header()
    
    # Vérifications préliminaires
    if not check_python_version():
        return False
    
    # Installation étape par étape
    steps = [
        create_directory_structure,
        create_requirements_txt,
        setup_virtual_environment,
        create_example_config,
        create_readme,
        create_launcher_script
    ]
    
    for step in steps:
        if not step():
            print(f"\n❌ ÉCHEC DE L'INSTALLATION à l'étape: {step.__name__}")
            return False
    
    # Instructions finales
    print_final_instructions()
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Installation interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
