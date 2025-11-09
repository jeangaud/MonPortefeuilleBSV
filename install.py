#!/usr/bin/env python3
"""
install.py - Script d'Installation BSV Wallet v4.0
==================================================

Ce script automatise l'installation complète du portefeuille modulaire.
Compatible uniquement avec Debian/Linux.
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def print_header():
    """Affiche l'en-tête d'installation."""
    print("=" * 60)
    print("🚀 INSTALLATION BSV WALLET v4.0 MODULAIRE")
    print("=" * 60)
    print()

def check_os():
    """Vérifie que le système d'exploitation est Linux/Debian."""
    print("🖥️ Vérification du système d'exploitation...")
    if sys.platform not in ('linux', 'linux2'):
        print(f"❌ Ce script nécessite Linux/Debian. OS détecté: {sys.platform}")
        print("⚠️ Windows et macOS ne sont pas supportés.")
        return False
    print(f"✅ Linux détecté ({platform.system()})")
    return True

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

        # Installer les dépendances en utilisant le Python du venv
        print("📦 Installation des dépendances...")
        pip_path = os.path.join("venv", "bin", "python")
        subprocess.run([pip_path, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dépendances installées")

        print(f"\n💡 Pour activer l'environnement virtuel:")
        print(f"   source venv/bin/activate")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la configuration: {e}")
        return False

def create_example_config():
    """Crée config.ini à partir du template config.ini.example."""
    print("\n⚙️ Préparation du fichier config.ini...")

    try:
        # Vérifier que config.ini.example existe
        if not os.path.exists("config.ini.example"):
            print("❌ Le fichier config.ini.example n'existe pas")
            print("⚠️ Assurez-vous de cloner le repository complet")
            return False

        # Copier config.ini.example en config.ini
        shutil.copy("config.ini.example", "config.ini")
        print("✅ config.ini créé à partir de config.ini.example")

        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création de config.ini: {e}")
        return False

def create_launcher_script():
    """Crée un script de lancement pour Linux."""
    print("\n🚀 Création du script de lancement...")

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

        # Rendre exécutable
        os.chmod(filename, 0o755)

        print(f"✅ {filename} créé et rendu exécutable")
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
    print()
    print("1. ⚙️  Configurez votre mnémonique dans config.ini")
    print("   Éditez le fichier et remplacez les valeurs par défaut")
    print()
    print("2. 🔄 Activez l'environnement virtuel:")
    print("   source venv/bin/activate")
    print()
    print("3. 🚀 Lancez le portefeuille:")
    print("   python main.py")
    print()
    print("💡 OU utilisez le script de lancement (plus simple):")
    print("   ./launch_wallet.sh")
    print()
    print("📖 Lisez README.md pour les instructions complètes")
    print()
    print("⚠️  IMPORTANT: Ne partagez JAMAIS votre mnémonique de 12 mots!")
    print("=" * 60)

def main():
    """Fonction principale d'installation."""
    print_header()

    # Vérifications préliminaires
    if not check_os():
        return False

    if not check_python_version():
        return False

    # Installation étape par étape
    steps = [
        create_directory_structure,
        create_requirements_txt,
        setup_virtual_environment,
        create_example_config,
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
