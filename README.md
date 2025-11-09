# BSV Wallet v4.0 - Modulaire

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
venv\Scripts\activate
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
