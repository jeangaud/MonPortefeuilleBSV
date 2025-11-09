"""
wallet_network.py
=================
Module de communication réseau pour BSV Wallet v4.0

Responsabilités:
- Communication avec les serveurs ElectrumX
- Requêtes RPC JSON
- Surveillance SPV en temps réel
- Gestion des connexions et erreurs réseau
"""

import socket
import ssl
import json
import time
from datetime import datetime
from decimal import Decimal

class WalletNetwork:
    """Gestionnaire de communication réseau pour le portefeuille BSV."""
    
    def __init__(self, server='electrumx.gorillapool.io', port=50002):
        self.server = server
        self.port = port
        self.satoshis_per_bsv = 100000000

#    def __init__(self, server='electrum.api.sv', port=50002):
#        self.server = server
#        self.port = port
#        self.satoshis_per_bsv = 100000000

#    def __init__(self, server='sv.satoshi.io', port=50002):
#        self.server = server
#        self.port = port
#        self.satoshis_per_bsv = 100000000


    def send_rpc_request(self, method, params):
        """Envoie une requête JSON-RPC générique au serveur ElectrumX."""
        try:
            request = {"method": method, "params": params, "id": 1}
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((self.server, self.port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=self.server) as ssock:
                    ssock.sendall(json.dumps(request).encode() + b'\n')
                    response_data = b""
                    while True:
                        part = ssock.recv(4096)
                        response_data += part
                        if len(part) < 4096 and response_data.endswith(b'\n'):
                            break
                    
                    response = json.loads(response_data.decode())
                    
                    if 'error' in response and response['error']:
                        print(f"ERREUR SERVEUR: {response['error']}")
                        return None
                        
                    return response.get("result")
        except Exception as e:
            print(f"ERREUR RPC: {e}")
            return None
    
    def get_balance(self, scripthash):
        """Récupère le solde d'un scripthash."""
        return self.send_rpc_request("blockchain.scripthash.get_balance", [scripthash])
    
    def get_utxos(self, scripthash):
        """Récupère les UTXOs d'un scripthash."""
        return self.send_rpc_request("blockchain.scripthash.listunspent", [scripthash])
    
    def get_history(self, scripthash):
        """Récupère l'historique des transactions d'un scripthash."""
        return self.send_rpc_request("blockchain.scripthash.get_history", [scripthash])
    
    def broadcast_transaction(self, raw_tx_hex):
        """Diffuse une transaction sur le réseau."""
        return self.send_rpc_request("blockchain.transaction.broadcast", [raw_tx_hex])
    
    def get_transaction(self, tx_hash, verbose=False):
        """Récupère les détails d'une transaction."""
        return self.send_rpc_request("blockchain.transaction.get", [tx_hash, verbose])
    
    def get_block_header(self, height_or_hash):
        """Récupère l'en-tête d'un bloc par hauteur ou hash."""
        try:
            if isinstance(height_or_hash, int):
                return self.send_rpc_request("blockchain.block.header", [height_or_hash])
            elif isinstance(height_or_hash, str) and len(height_or_hash) == 64:
                # Essayer avec le hash directement
                try:
                    return self.send_rpc_request("blockchain.block.header", [height_or_hash])
                except:
                    # Si ça ne marche pas, on ne peut pas continuer
                    return None
            return None
        except Exception as e:
            print(f"Erreur get_block_header: {e}")
            return None
    
    def get_block_hash(self, height):
        """Récupère le hash d'un bloc par sa hauteur."""
        try:
            return self.send_rpc_request("blockchain.block.get_hash", [height])
        except Exception as e:
            print(f"Erreur get_block_hash: {e}")
            return None
    
    def get_block_height(self, block_hash):
        """Récupère la hauteur d'un bloc par son hash."""
        try:
            # Cette méthode peut ne pas être supportée par tous les serveurs
            return self.send_rpc_request("blockchain.block.height", [block_hash])
        except Exception as e:
            print(f"Méthode blockchain.block.height non supportée: {e}")
            return None
    
    def get_merkle_proof(self, tx_hash, block_height_or_hash):
        """Récupère la preuve Merkle d'une transaction."""
        try:
            return self.send_rpc_request("blockchain.transaction.get_merkle", [tx_hash, block_height_or_hash])
        except Exception as e:
            print(f"Erreur get_merkle_proof: {e}")
            return None

class SPVMonitor:
    """Moniteur SPV pour surveiller les adresses en temps réel."""
    
    def __init__(self, network):
        self.network = network
        self.satoshis_per_bsv = 100000000
    
    def monitor_address(self, address, scripthash, expected_amount=None, check_interval=3, show_periodic=True):
        """Surveille une adresse pour les transactions entrantes."""
        print(f"\n🔍 MODE SPV ACTIVÉ - Surveillance de l'adresse:")
        print(f"   {address}")
        if expected_amount:
            print(f"   Montant attendu: {expected_amount:.8f} BSV")
        print(f"   Temps: {datetime.now().strftime('%H:%M:%S')}")
        print("\n⏳ En attente de transactions... (Ctrl+C pour arrêter)")
        
        # Obtenir l'état initial
        initial_balance = self.network.get_balance(scripthash)
        last_balance = initial_balance.get('confirmed', 0) + initial_balance.get('unconfirmed', 0) if initial_balance else 0
        
        print(f"📊 Solde initial: {Decimal(last_balance) / self.satoshis_per_bsv:.8f} BSV")
        print("-" * 50)
        
        check_count = 0
        try:
            while True:
                time.sleep(check_interval)
                check_count += 1
                
                # Vérifier le solde actuel
                current_balance_info = self.network.get_balance(scripthash)
                if not current_balance_info:
                    continue
                
                confirmed = current_balance_info.get('confirmed', 0)
                unconfirmed = current_balance_info.get('unconfirmed', 0)
                current_balance = confirmed + unconfirmed
                
                # Afficher un point toutes les 10 vérifications pour montrer l'activité
                if show_periodic and check_count % 10 == 0:
                    print(f"• Vérification #{check_count} - {datetime.now().strftime('%H:%M:%S')}")
                
                # Détecter les changements
                if current_balance != last_balance:
                    change = current_balance - last_balance
                    print(f"\n🎉 TRANSACTION DÉTECTÉE!")
                    print(f"   Temps: {datetime.now().strftime('%H:%M:%S')}")
                    print(f"   Changement: {'+' if change > 0 else ''}{Decimal(change) / self.satoshis_per_bsv:.8f} BSV")
                    print(f"   Nouveau solde: {Decimal(current_balance) / self.satoshis_per_bsv:.8f} BSV")
                    
                    if confirmed != current_balance:
                        print(f"   Confirmé: {Decimal(confirmed) / self.satoshis_per_bsv:.8f} BSV")
                        print(f"   Non confirmé: {Decimal(unconfirmed) / self.satoshis_per_bsv:.8f} BSV")
                    
                    # Vérifier si c'est le montant attendu
                    if expected_amount and abs(Decimal(change) / self.satoshis_per_bsv - expected_amount) < Decimal('0.00000001'):
                        print(f"✅ MONTANT ATTENDU REÇU!")
                        
                        # Demander si on continue la surveillance
                        try:
                            continue_monitoring = input("\nContinuer la surveillance? (o/n): ").lower()
                            if continue_monitoring != 'o':
                                break
                        except:
                            break
                    
                    last_balance = current_balance
                    print("-" * 50)
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 Surveillance arrêtée par l'utilisateur")
            print(f"   Durée: {check_count * check_interval} secondes ({check_count} vérifications)")
            
            # Obtenir le solde final
            final_balance_info = self.network.get_balance(scripthash)
            if final_balance_info:
                final_balance = final_balance_info.get('confirmed', 0) + final_balance_info.get('unconfirmed', 0)
                print(f"   Solde final: {Decimal(final_balance) / self.satoshis_per_bsv:.8f} BSV")
        
        return True
