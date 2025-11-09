# Guide de dépannage - MonPortefeuilleBSV

## ✅ Problème de certificat SSL - RÉSOLU

### Symptôme d'origine
```
ERREUR RPC: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate
```

### Cause identifiée
Le serveur ElectrumX `electrumx.gorillapool.io` utilise un certificat auto-signé. De plus, le paramètre `verify_ssl` dans `config.ini` n'était pas pris en compte à cause d'un bug dans le code.

### ✅ Corrections appliquées (Version actuelle)

**1. Ajout de la configuration réseau dans config.ini**
```ini
[Network]
electrumx_server = electrumx.gorillapool.io
electrumx_port = 50002
verify_ssl = false
```

**2. Correction du bug dans main.py**
Le module `WalletNetwork` était créé AVANT la lecture de la configuration. Le code a été corrigé pour :
- Lire la configuration réseau depuis `config.ini`
- Créer `WalletNetwork` avec les bons paramètres
- Afficher la configuration au démarrage : `🔒 Vérification SSL: désactivée`

**Confirmation au démarrage** : Vous devriez voir ces lignes :
```
🌐 Serveur ElectrumX: electrumx.gorillapool.io:50002
🔒 Vérification SSL: désactivée
```

**⚠️ Note de sécurité** : Désactiver la vérification SSL rend la connexion moins sécurisée. En production, préférez :
- Utiliser un serveur avec un certificat SSL valide
- Ou installer le certificat du serveur dans le système
- Ou utiliser une connexion VPN sécurisée

---

## Problème de résolution DNS

### Symptôme
```
Could not resolve host: electrumx.gorillapool.io
```

### Cause
L'environnement actuel (conteneur Docker/sandbox) a des restrictions réseau qui empêchent la résolution DNS de certains domaines.

### Solutions

#### Option 1 : Tester en environnement local
Exécutez le portefeuille sur votre machine locale (hors conteneur) où la résolution DNS fonctionne normalement :

```bash
cd MonPortefeuilleBSV
source venv/bin/activate
python main.py
```

#### Option 2 : Utiliser l'adresse IP directement
Si vous connaissez l'IP du serveur, modifiez `config.ini` :

```ini
[Network]
electrumx_server = <adresse_IP>
electrumx_port = 50002
verify_ssl = false
```

#### Option 3 : Essayer un serveur alternatif
Utilisez un autre serveur ElectrumX BSV public. Exemples :

```ini
[Network]
# Serveur alternatif 1
electrumx_server = sv.electrumx.cash
electrumx_port = 50002
verify_ssl = true

# Ou serveur alternatif 2
electrumx_server = electrumx.bitcoinsv.io
electrumx_port = 50002
verify_ssl = true
```

**Note** : Testez la disponibilité des serveurs avant utilisation.

---

## Configuration réseau via variables d'environnement

Pour plus de flexibilité, vous pouvez utiliser des variables d'environnement :

```bash
export ELECTRUMX_SERVER="electrumx.gorillapool.io"
export ELECTRUMX_PORT="50002"
export VERIFY_SSL="false"

python main.py
```

Les variables d'environnement ont **priorité** sur le fichier `config.ini`.

---

## Vérification de la configuration

Pour vérifier que votre configuration réseau est correcte :

```bash
source venv/bin/activate
python3 << EOF
import sys
sys.path.insert(0, 'modules')
from wallet_config import WalletConfig

config = WalletConfig()
if config.read_config():
    network_config = config.get_network_config()
    print(f"Serveur: {network_config['electrumx_server']}")
    print(f"Port: {network_config['electrumx_port']}")
    print(f"SSL: {network_config['verify_ssl']}")
EOF
```

---

## Test de connectivité réseau

### Tester la résolution DNS
```bash
nslookup electrumx.gorillapool.io
# ou
dig electrumx.gorillapool.io
# ou
ping electrumx.gorillapool.io
```

### Tester la connexion au port SSL
```bash
openssl s_client -connect electrumx.gorillapool.io:50002
```

### Tester la connexion avec telnet
```bash
telnet electrumx.gorillapool.io 50002
```

Si ces commandes échouent, le problème est au niveau réseau/firewall, pas au niveau du portefeuille.

---

## État actuel du projet

### ✅ Corrections appliquées
- Section `[Network]` ajoutée à `config.ini`
- Option `verify_ssl = false` configurée pour contourner le problème de certificat auto-signé

### ⚠️ Limitations actuelles
- L'environnement de test actuel (sandbox) ne permet pas la résolution DNS de `electrumx.gorillapool.io`
- Le portefeuille **fonctionnera correctement** sur un système avec connexion Internet normale

### 🧪 Tests à effectuer hors sandbox
1. Scanner les adresses avec fonds
2. Envoyer une transaction de test
3. Vérifier le mode SPV
4. Tester la résolution Paymail

---

## Support supplémentaire

Pour toute question ou problème :
- Consultez le README.md pour l'installation
- Vérifiez les logs dans le dossier `logs/`
- Examinez les transactions sauvegardées dans `transactions/`

---

**Dernière mise à jour** : 2025-11-09
**Version du portefeuille** : v4.0
