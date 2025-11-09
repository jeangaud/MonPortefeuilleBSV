# 🏗️ BSV Wallet v4.0 - Structure Modulaire

## 📁 Structure du Projet

```
BSV_Wallet_v4/
├── 🐍 main.py                    # Point d'entrée principal
├── 📄 config.ini                 # Configuration utilisateur
├── 📁 modules/                   # Modules Python
│   ├── 🔧 wallet_config.py       # Gestion configuration
│   ├── 🔐 wallet_crypto.py       # Cryptographie BIP39/32
│   ├── 🌐 wallet_network.py      # Communication réseau
│   ├── 💰 wallet_transaction.py  # Création transactions
│   ├── 🔍 wallet_scanner.py      # Scanner d'adresses
│   └── 🖥️  wallet_ui.py          # Interface utilisateur
├── 📁 transactions/              # Transactions sauvegardées
├── 📁 logs/                      # Logs (optionnel)
└── 📄 requirements.txt           # Dépendances Python
```

## 🎯 Responsabilités des Modules

### 🔧 wallet_config.py
**Gestion de la Configuration**
- ✅ Lecture/écriture `config.ini`
- ✅ Validation des paramètres
- ✅ Création configuration par défaut
- ✅ Gestion des erreurs de config
- ✅ Status de configuration pour UI

**Méthodes principales:**
- `read_config()` - Lit config.ini
- `validate_mnemonic()` - Valide la mnémonique
- `get_transaction_config()` - Config de transaction
- `create_default_config()` - Crée config par défaut

### 🔐 wallet_crypto.py
**Cryptographie et Adresses**
- ✅ Génération d'adresses HD (BIP32)
- ✅ Conversion adresse/scripthash
- ✅ Validation d'adresses
- ✅ Utilitaires cryptographiques Bitcoin
- ✅ Gestion clés privées/publiques

**Méthodes principales:**
- `initialize_from_mnemonic()` - Init depuis mnémonique
- `get_address_info()` - Info adresse par index
- `address_to_scripthash()` - Conversion pour ElectrumX
- `validate_address()` - Validation adresses

### 🌐 wallet_network.py
**Communication Réseau**
- ✅ Communication ElectrumX (RPC JSON)
- ✅ Surveillance SPV temps réel
- ✅ Broadcast de transactions
- ✅ Récupération balances/UTXOs
- ✅ Gestion erreurs réseau

**Classes:**
- `WalletNetwork` - Communication de base
- `SPVMonitor` - Surveillance temps réel

**Méthodes principales:**
- `send_rpc_request()` - Requêtes ElectrumX
- `get_balance()` - Solde d'une adresse
- `broadcast_transaction()` - Diffusion TX
- `monitor_address()` - Surveillance SPV

### 💰 wallet_transaction.py
**Gestion des Transactions**
- ✅ Création transactions multi-adresses
- ✅ Sélection optimale d'UTXOs
- ✅ Signatures BSV (SIGHASH_FORKID)
- ✅ Gestion des frais et du change
- ✅ Validation signatures canoniques

**Méthodes principales:**
- `select_utxos_for_amount()` - Sélection UTXOs
- `create_multi_address_transaction()` - Création TX
- `create_bch_sighash()` - Sighash BIP143
- `is_canonical_signature()` - Validation signatures

### 🔍 wallet_scanner.py
**Scanner d'Adresses**
- ✅ Scan des adresses HD pour fonds
- ✅ Récupération balances/UTXOs
- ✅ Optimisation des requêtes réseau
- ✅ Formatage des résultats
- ✅ Vérification rapide d'adresses

**Méthodes principales:**
- `scan_all_addresses()` - Scan complet
- `get_single_address_info()` - Info adresse unique
- `check_address_has_funds()` - Vérification rapide
- `format_balance_display()` - Formatage pour UI

### 🖥️ wallet_ui.py
**Interface Utilisateur**
- ✅ Menu principal interactif
- ✅ Menus de sous-fonctions
- ✅ Gestion entrées utilisateur
- ✅ Affichage formaté des résultats
- ✅ Messages d'aide et d'erreur

**Méthodes principales:**
- `show_main_menu()` - Menu principal
- `menu_check_balance()` - Menu balance
- `menu_send_funds()` - Menu envoi
- `menu_receive_funds()` - Menu réception SPV
- `menu_configuration()` - Menu config

## 🔄 Flux d'Exécution

### 1. Initialisation
```python
main.py → BSVWalletManager() → initialize()
├── WalletConfig.read_config()
├── WalletConfig.validate_mnemonic()
└── WalletCrypto.initialize_from_mnemonic()
```

### 2. Menu Principal
```python
WalletUI.show_main_menu()
├── Option 1: Balance → WalletScanner.scan_all_addresses()
├── Option 2: Envoi → TransactionBuilder.create_transaction()
├── Option 3: Réception → SPVMonitor.monitor_address()
└── Option 4: Config → WalletConfig.get_config_status()
```

### 3. Envoi de Fonds
```python
WalletManager.send_funds()
├── WalletScanner.scan_all_addresses()
├── TransactionBuilder.select_utxos_for_amount()
├── TransactionBuilder.create_multi_address_transaction()
└── WalletNetwork.broadcast_transaction()
```

### 4. Surveillance SPV
```python
WalletManager.monitor_address_spv()
├── WalletCrypto.address_to_scripthash()
└── SPVMonitor.monitor_address()
    ├── WalletNetwork.get_balance() (boucle)
    └── Détection changements temps réel
```

## 🛠️ Installation et Configuration

### 1. Créer la Structure
```bash
mkdir BSV_Wallet_v4
cd BSV_Wallet_v4
mkdir modules transactions logs
```

### 2. Copier les Fichiers
- `main.py` → Racine du projet
- Tous les `wallet_*.py` → Dossier `modules/`
- `config.ini` → Racine du projet

### 3. Installer les Dépendances
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

pip install bip-utils base58 ecdsa configparser
```

### 4. Configurer config.ini
```ini
[Credentials]
mnemonic = your twelve word mnemonic phrase goes here exactly as given
passcode = 

[Transaction]
destination_address = 1DestinationAddressGoesHere
amount_to_send_bsv = 0.001
fee_per_byte = 1

[SPV]
check_interval = 3
show_periodic_checks = true
```

### 5. Lancer le Programme
```bash
python3 main.py
```

## ✨ Avantages de cette Structure

### 🎯 **Modularité**
- Chaque module a une responsabilité claire
- Facilite les tests unitaires
- Permet la réutilisation de code

### 🔧 **Maintenabilité**
- Code organisé et documenté
- Facile à modifier/étendre
- Séparation des préoccupations

### 🚀 **Évolutivité**
- Nouveaux modules faciles à ajouter
- Structure prête pour fonctionnalités avancées
- Intégration d'APIs externes simplifiée

### 🧪 **Testabilité**
- Chaque module peut être testé séparément
- Mocking facile des dépendances
- Tests d'intégration simplifiés

## 🔮 Évolutions Futures Possibles

### Modules Additionnels
- **wallet_qr.py** - Génération de QR codes
- **wallet_backup.py** - Sauvegarde automatique
- **wallet_exchange.py** - Intégration APIs exchanges
- **wallet_multisig.py** - Transactions multisig
- **wallet_lightning.py** - Lightning Network
- **wallet_notifications.py** - Alertes email/SMS
- **wallet_analytics.py** - Statistiques portefeuille
- **wallet_hardware.py** - Support hardware wallets

### Fonctionnalités Avancées
- **Interface graphique** (Tkinter, PyQt)
- **API REST** pour contrôle distant
- **Base de données** pour historique
- **Chiffrement** des fichiers de config
- **Support multi-devises** (BTC, BCH, etc.)

## 📝 Notes pour le Développement

### Structure Recommandée pour Évolutions
```python
# Nouveau module exemple: wallet_qr.py
class QRCodeGenerator:
    def __init__(self, crypto_manager):
        self.crypto = crypto_manager
    
    def generate_qr_for_address(self, address, amount=None):
        # Génération QR code
        pass

# Integration dans main.py
from wallet_qr import QRCodeGenerator

class BSVWalletManager:
    def __init__(self):
        # ... modules existants ...
        self.qr_generator = QRCodeGenerator(self.crypto)
```

### Bonnes Pratiques
- **Toujours documenter** les nouvelles fonctions
- **Gérer les erreurs** proprement
- **Tester** avant de merger
- **Respecter** la séparation des responsabilités
- **Utiliser** les modules existants quand possible

Cette structure modulaire facilite grandement l'évolution et la maintenance du portefeuille BSV ! 🎉
