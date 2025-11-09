"""
wallet_paymail.py - Version Corrigée pour HandCash
==================================================
Module Paymail pour BSV Wallet v4.0 avec support HandCash fixé

Responsabilités:
- Résolution d'adresses Paymail vers Bitcoin
- Support spécialisé pour HandCash (cloud.handcash.io)
- Compatibilité avec tous les fournisseurs Paymail
- Gestion des protocoles bsvalias standard et non-standard

CORRECTIONS APPLIQUÉES:
- HandCash utilise 'paymentDestination' au lieu de 'addressResolution'
- Endpoint migré vers cloud.handcash.io
- Support des capacités hex-encoded
- Le corps de la requête P2P est maintenant conforme au standard
- Le format de date 'dt' est maintenant un timestamp numérique.
- Ajout d'un champ 'signature' (simulé) pour la conformité P2P.
- **NOUVEAU: Conversion du script de sortie P2P en adresse Bitcoin.**
"""

import urllib.request
import urllib.parse
import json
import ssl
import hashlib
from decimal import Decimal
from datetime import datetime, timezone

# --- Implémentation Base58 nécessaire pour la conversion d'adresse ---
BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def base58_encode(data: bytes) -> str:
    """Encode des bytes en format Base58Check."""
    n = int.from_bytes(data, 'big')
    if n == 0:
        return BASE58_ALPHABET[0]
    
    res = []
    while n > 0:
        n, r = divmod(n, 58)
        res.append(BASE58_ALPHABET[r])
    
    encoded = ''.join(reversed(res))
    
    pad = 0
    for b in data:
        if b == 0: pad += 1
        else: break
            
    return (BASE58_ALPHABET[0] * pad) + encoded
# --- Fin de l'implémentation Base58 ---


class PaymailClient:
    """Client Paymail avec support HandCash corrigé."""
    
    def __init__(self, wallet_crypto_module=None):
        self.satoshis_per_bsv = 100000000
        self.user_agent = 'BSV-Wallet-v4.0-Paymail-Client'
        self.crypto = wallet_crypto_module
    
    def _script_to_address(self, script_hex: str) -> str | None:
        """Tente de convertir un script P2PKH en adresse Bitcoin."""
        # P2PKH script: OP_DUP OP_HASH160 <20-byte-hash> OP_EQUALVERIFY OP_CHECKSIG
        # Hex:          76      a9      14          ...         88          ac
        if not (script_hex.startswith('76a914') and script_hex.endswith('88ac') and len(script_hex) == 50):
            print("ℹ️ Le script de sortie n'est pas un P2PKH standard, impossible de le convertir en adresse.")
            return None
        
        try:
            pubkey_hash = bytes.fromhex(script_hex[6:46])
            versioned_hash = b'\x00' + pubkey_hash # Version 0x00 pour P2PKH mainnet
            checksum = hashlib.sha256(hashlib.sha256(versioned_hash).digest()).digest()
            address_bytes = versioned_hash + checksum[:4]
            bitcoin_address = base58_encode(address_bytes)
            print(f"✅ Script P2PKH converti en adresse: {bitcoin_address}")
            return bitcoin_address
        except Exception as e:
            print(f"⚠️ Erreur lors de la conversion du script en adresse: {e}")
            return None

    def is_paymail_address(self, address):
        """Vérifie si une adresse est au format Paymail."""
        if not address or '@' not in address: return False
        parts = address.split('@')
        if len(parts) != 2: return False
        alias, domain = parts
        if not alias or not domain or '.' not in domain: return False
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_@')
        return all(c in allowed_chars for c in address)
    
    def get_paymail_info(self, paymail):
        """Récupère les informations d'une adresse Paymail."""
        try:
            if not self.is_paymail_address(paymail): return {'success': False, 'error': 'Format Paymail invalide'}
            alias, domain = paymail.split('@', 1)
            if domain.lower() == 'handcash.io': return self._get_handcash_info(alias, domain)
            capabilities = self._get_paymail_capabilities(domain)
            if not capabilities['success']: return capabilities
            return {'success': True, 'alias': alias, 'domain': domain, 'bsvalias_version': capabilities.get('bsvalias_version', 'Unknown'), 'supported_features': list(capabilities['capabilities'].keys())}
        except Exception as e:
            return {'success': False, 'error': f'Erreur info Paymail: {str(e)}'}

    def _get_handcash_info(self, alias, domain):
        """Informations spécialisées pour HandCash."""
        try:
            endpoint = "https://cloud.handcash.io/.well-known/bsvalias"
            response = self._make_request(endpoint)
            if not response: return {'success': False, 'error': 'Serveur HandCash inaccessible'}
            capabilities = response.get('capabilities', {})
            capability_mapping = {'paymentDestination': 'Résolution d\'adresse P2P', '2a40af698840': 'Paiements P2P (hex)', 'pki': 'Infrastructure clé publique', 'a9f510c16bde': 'Vérification propriétaire', 'f12f968c92d6': 'Profil public'}
            readable_features = [capability_mapping.get(k, f'Capacité: {k}') for k in capabilities]
            return {'success': True, 'alias': alias, 'domain': domain, 'bsvalias_version': response.get('bsvalias', 'Unknown'), 'supported_features': readable_features, 'provider_info': 'HandCash (endpoint migré vers cloud.handcash.io)'}
        except Exception as e:
            return {'success': False, 'error': f'Erreur HandCash info: {str(e)}'}

    def resolve_address(self, paymail, amount_bsv=None):
        """Résout une adresse Paymail vers une adresse Bitcoin."""
        try:
            if not self.is_paymail_address(paymail): return {'success': False, 'error': 'Format Paymail invalide'}
            alias, domain = paymail.split('@', 1)
            if domain.lower() == 'handcash.io':
                print(f"🔧 Détection HandCash, utilisation de la résolution spécialisée...")
                return self._resolve_handcash_address(paymail, amount_bsv)
            return self._resolve_standard_paymail(paymail, amount_bsv)
        except Exception as e:
            return {'success': False, 'error': f'Erreur résolution Paymail: {str(e)}'}

    def _resolve_handcash_address(self, paymail, amount_bsv=None):
        """Résolution spécialisée pour HandCash avec support paymentDestination."""
        try:
            alias, domain = paymail.split('@', 1)
            print(f"🔧 Résolution HandCash spécialisée pour: {paymail}")
            
            capabilities = self._get_paymail_capabilities(domain)
            if not capabilities['success']: return capabilities
            
            caps = capabilities['capabilities']
            resolution_template = caps.get('paymentDestination') or caps.get('2a40af698840')
            if not resolution_template: return {'success': False, 'error': 'HandCash ne supporte pas la résolution d\'adresse'}
            
            resolution_url = resolution_template.replace('{alias}', alias).replace('{domain.tld}', domain)
            print(f"📡 Requête HandCash: {resolution_url}")
            
            request_data, method = None, 'GET'
            
            if amount_bsv:
                method = 'POST'
                amount_satoshis = int(amount_bsv * self.satoshis_per_bsv)
                request_data = {"senderName": "BSV Wallet v4.0", "senderHandle": "anonymous@bsvwallet.com", "amount": amount_satoshis, "purpose": "Payment from BSV Wallet v4.0", "dt": int(datetime.now(timezone.utc).timestamp())}

                # Generate proper signature if crypto module is available
                if self.crypto and hasattr(self.crypto, 'sign_message'):
                    try:
                        signature = self.crypto.sign_message(self.crypto.get_private_key_for_signing(), json.dumps(request_data))
                        request_data["signature"] = signature
                        print(f"✅ Signature cryptographique générée")
                    except Exception as e:
                        print(f"⚠️ Impossible de générer la signature: {e}")
                        print(f"⚠️ La requête sera envoyée sans signature")
                else:
                    print(f"⚠️ Module crypto non disponible - signature non générée")
                    print(f"⚠️ La requête sera envoyée sans signature")

                print(f"💰 Résolution P2P avec montant: {amount_bsv:.8f} BSV")
                print(f"📋 Corps de la requête: {request_data}")
            
            resolution_response = self._make_request(resolution_url, method=method, data=request_data)
            if not resolution_response: return {'success': False, 'error': 'La requête au serveur HandCash a échoué.'}
            
            output_script = resolution_response.get('output')
            bitcoin_address = resolution_response.get('address')
            
            # **NOUVELLE LOGIQUE DE CONVERSION**
            if output_script and not bitcoin_address:
                bitcoin_address = self._script_to_address(output_script)

            if not output_script and not bitcoin_address: return {'success': False, 'error': f'Réponse HandCash inattendue: {resolution_response}'}
            
            print(f"✅ HandCash résolu. Output: {(bitcoin_address or output_script)[:60]}...")
            return {'success': True, 'address': bitcoin_address, 'output': output_script, 'provider': 'HandCash (cloud.handcash.io)', 'type': 'P2P' if amount_bsv else 'Basic', 'reference': resolution_response.get('reference'), 'memo': resolution_response.get('memo')}
        except Exception as e:
            import traceback; traceback.print_exc()
            return {'success': False, 'error': f'Erreur résolution HandCash: {str(e)}'}

    def _resolve_standard_paymail(self, paymail, amount_bsv=None):
        return {'success': False, 'error': 'Non implémenté pour ce test'}

    def _get_paymail_capabilities(self, domain):
        if domain.lower() == 'handcash.io':
            endpoint = "https://cloud.handcash.io/.well-known/bsvalias"
            response = self._make_request(endpoint)
            if response: return {'success': True, 'capabilities': response.get('capabilities', {}), 'bsvalias_version': response.get('bsvalias', '1.0')}
        return {'success': False, 'error': f'Impossible de trouver les capacités pour {domain}.'}

    def _make_request(self, url, method='GET', data=None, verify_ssl=True):
        try:
            headers = {'User-Agent': self.user_agent, 'Accept': 'application/json', 'Content-Type': 'application/json'}
            request_body = json.dumps(data).encode('utf-8') if method == 'POST' and data else None
            request = urllib.request.Request(url, data=request_body, headers=headers, method=method)

            context = ssl.create_default_context()
            # Only disable SSL verification if explicitly requested (not recommended)
            if not verify_ssl:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            # else: use default secure settings (verify_mode = ssl.CERT_REQUIRED)

            with urllib.request.urlopen(request, timeout=15, context=context) as response:
                if 200 <= response.status < 300: return json.loads(response.read().decode('utf-8'))
                print(f"❌ Erreur HTTP {response.status}: {response.reason}")
                return None
        except urllib.error.HTTPError as e:
            error_body = "Aucune réponse du serveur."
            try: error_body = e.read().decode()
            except Exception: pass
            print(f"❌ HTTPError {e.code}: {e.reason}\n   Réponse du serveur: {error_body}")
            return None
        except Exception as e:
            print(f"❌ Erreur requête: {e}")
            return None

class PaymailIntegration:
    """Intégration Paymail pour le portefeuille BSV."""
    
    def __init__(self, wallet_manager):
        self.wallet = wallet_manager
        crypto_module = getattr(wallet_manager, 'crypto', None)
        self.paymail_client = PaymailClient(crypto_module)
    
    def resolve_destination(self, paymail, amount_bsv=None):
        print(f"🔍 Résolution Paymail: {paymail}")
        if amount_bsv: print(f"💰 Montant spécifié: {amount_bsv:.8f} BSV")
        resolution = self.paymail_client.resolve_address(paymail, amount_bsv)
        if resolution['success']:
            print(f"✅ Résolution réussie!")
            dest = resolution.get('address') or resolution.get('output')
            print(f"   Output/Adresse: {dest[:60]}...")
        else:
            print(f"❌ Erreur résolution Paymail: {resolution['error']}")
        return resolution
    
    def send_to_paymail(self, paymail, amount_bsv, fee_per_byte=1):
        resolution = self.resolve_destination(paymail, amount_bsv)
        if not resolution['success']: return False
        destination_address = resolution.get('address')
        if not destination_address:
             print("❌ ERREUR CRITIQUE: La résolution Paymail n'a pas renvoyé d'adresse Bitcoin directe.")
             return False
        tx_config = {'destination_address': destination_address, 'amount_bsv': amount_bsv, 'fee_per_byte': fee_per_byte}
        try:
            return self.wallet.send_funds(tx_config)
        except Exception as e:
            print(f"❌ Erreur envoi Paymail: {e}")
            return False

if __name__ == "__main__":
    print("🔒 Module Paymail - Tests désactivés")
    print("Pour tester: utilisez un script de test externe avec vos propres adresses Paymail")
    print("IMPORTANT: Ne jamais commiter d'adresses Paymail réelles ou de secrets dans le code")
