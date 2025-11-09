# BSV Wallet v4.0 - Modulaire

Un portefeuille Bitcoin SV (BSV) sécurisé, modulaire et complet avec support HandCash Paymail.

## 📋 Table des matières

- [Installation](#installation)
- [Configuration](#configuration)
- [Démarrage Rapide](#démarrage-rapide)
- [Fonctionnalités](#fonctionnalités)
- [Sécurité](#sécurité)
- [Architecture](#structure-du-projet)
- [Variables d'environnement](#variables-denvironnement)

## 🔧 Installation

### Prérequis

- **Debian/Linux** (testé sur Debian)
- **Python 3.8+** installé
- **pip** (gestionnaire de paquets Python)
- **Git** (pour cloner le repository)

Installation rapide des dépendances système :
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv git
```

### Étapes d'installation

#### 1. Cloner le repository

```bash
git clone https://github.com/jeangaud/MonPortefeuilleBSV.git
cd MonPortefeuilleBSV
```

#### 2. Créer un environnement virtuel Python

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

#### 4. Préparer la configuration

```bash
# Copier le fichier exemple en configuration réelle
cp config.ini.example config.ini
```

**Important**: Le fichier `config.ini` ne sera jamais commité sur Git pour éviter les fuites de secrets.

#### 5. Éditer la configuration

Éditez `config.ini` et complétez les champs requis :

```ini
[Credentials]
# Votre mnémonique BIP39 (12 mots) - GARDEZ CECI SECRET!
mnemonic = word1 word2 word3 ... word12

# Passcode optionnel (laisser vide si aucun)
passcode =

[Transaction]
# Votre adresse Paymail pour recevoir les paiements
destination_address = username@handcash.io

# Montant à envoyer en BSV
amount_to_send_bsv = 0.01

# Frais réseau (1-2 satoshis/byte recommandé)
fee_per_byte = 1

[Network]
# Serveur ElectrumX pour la connexion réseau
electrumx_server = electrumx.gorillapool.io
electrumx_port = 50002

# Vérification SSL (recommandé: true)
verify_ssl = true
```

## 🚀 Démarrage Rapide

Une fois configuré, lancez simplement :

```bash
# Assurez-vous que l'environnement virtuel est activé
source venv/bin/activate

# Lancer le portefeuille
python main.py
```

Le portefeuille affichera un menu interactif pour :
- Afficher votre solde
- Envoyer des transactions
- Surveiller les transactions (mode SPV)
- Voir l'historique

## 🔧 Fonctionnalités

- ✅ **Portefeuille multi-adresses** - Gestion automatique des UTXOs
- ✅ **Mode SPV** - Surveillance temps réel avec notifications
- ✅ **Support Paymail** - Intégration HandCash complète
- ✅ **Interface interactive** - Menu user-friendly
- ✅ **Architecture modulaire** - Code organisé et maintenable
- ✅ **Signatures BSV** - Support complet Bitcoin SV

## 🔐 Sécurité

### Bonnes pratiques

1. **Protégez votre mnémonique**
   - Ne la partagez jamais
   - Ne la mettez pas dans des messages
   - Gardez-la offline si possible

2. **Variables d'environnement**
   - Utilisez des variables d'environnement pour les secrets sensibles
   - Ne commitez jamais `config.ini` avec des vraies données

3. **Testez d'abord**
   - Testez avec de petits montants
   - Vérifiez toutes les transactions avant de les envoyer

4. **Sauvegarde de secours**
   - Sauvegardez votre mnémonique dans un endroit sûr (offline)
   - Testez votre sauvegarde régulièrement

### Sécurité SSL/TLS

Par défaut, le portefeuille vérifie les certificats SSL/TLS de tous les serveurs.

```bash
# Vérification SSL activée par défaut (recommandé)
export VERIFY_SSL=true

# Si vous devez désactiver (NOT RECOMMENDED)
export VERIFY_SSL=false
```

## 📦 Variables d'environnement

Pour une configuration flexible et sécurisée, utilisez des variables d'environnement :

```bash
# Serveur ElectrumX
export ELECTRUMX_SERVER=electrumx.gorillapool.io
export ELECTRUMX_PORT=50002

# Vérification SSL
export VERIFY_SSL=true

# Données sensibles (alternative à config.ini)
export MNEMONIC="your twelve word mnemonic phrase"
export PASSCODE=""
```

## 📁 Structure du Projet

```
MonPortefeuilleBSV/
├── main.py                      # Point d'entrée principal
├── config.ini                   # Configuration (⚠️ ignoré par Git)
├── config.ini.example           # Modèle de configuration
├── requirements.txt             # Dépendances Python
├── .gitignore                   # Fichiers ignorés par Git
├── README.md                    # Ce fichier
├── modules/                     # Modules Python
│   ├── wallet_config.py         # Gestion de configuration
│   ├── wallet_crypto.py         # Cryptographie et signatures
│   ├── wallet_network.py        # Communication ElectrumX
│   ├── wallet_transaction.py    # Construction de transactions
│   ├── wallet_paymail.py        # Résolution Paymail/HandCash
│   ├── wallet_scanner.py        # Scanner d'adresses BIP44
│   ├── wallet_ui.py             # Interface utilisateur
│   └── ui/                      # Composants UI
├── transactions/                # Transactions sauvegardées
├── logs/                        # Fichiers journaux
└── venv/                        # Environnement virtuel (à créer)
```

## 🛠️ Dépannage

### Erreur: "Module crypto not available"
Assurez-vous que toutes les dépendances sont installées :
```bash
pip install -r requirements.txt
```

### Erreur: "Configuration not loaded"
Vérifiez que `config.ini` existe et contient une mnémonique valide de 12 mots.

### Erreur de connexion réseau
Vérifiez que :
- Votre connexion Internet fonctionne
- Le serveur ElectrumX est accessible
- Les pare-feu n'bloquent pas le port 50002

## 📖 Ressources

- [Bitcoin SV](https://bitcoinsv.io/)
- [BIP39 - Mnémoniques](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki)
- [BIP44 - Dérivation](https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki)
- [HandCash](https://handcash.io/)
- [ElectrumX Server](https://github.com/kyuupichan/ElectrumX)

## 📄 Licence

Ce projet est fourni à titre éducatif et de développement.

## 📞 Support

Pour les issues techniques, consultez la documentation du projet ou les logs d'application.

---

**⚠️ AVERTISSEMENT**: Ce portefeuille gère des fonds réels. Testez toujours avec des petits montants d'abord et sécurisez correctement votre mnémonique.

BSV Wallet v4.0 - Architecture Modulaire 🚀
