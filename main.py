#!/usr/bin/env python3
"""
main.py - BSV Wallet v4.0 Modulaire avec support Paymail
=========================================================
"""

import sys
import os
from decimal import Decimal
from datetime import datetime # NOUVEAU: Import pour le timestamp du cache

# Ajouter le dossier modules au path Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

# Importer tous les modules
try:
    from wallet_config import WalletConfig
    from wallet_crypto import WalletCrypto
    from wallet_network import WalletNetwork, SPVMonitor
    from wallet_transaction import TransactionBuilder
    from wallet_scanner import WalletScanner
    from wallet_ui import WalletUI
    from wallet_spv_complete import TrueSPVClient, add_true_spv_to_wallet
    from wallet_paymail import PaymailIntegration
except ImportError as e:
    print(f"❌ ERREUR: Impossible d'importer les modules: {e}")
    sys.exit(1)

class BSVWalletManager:
    """
    Gestionnaire principal du portefeuille BSV v4.0 avec support Paymail
    Orchestre tous les modules et gère le flux principal d'exécution.
    """
    
    def __init__(self):
        # Initialiser tous les modules
        self.config = WalletConfig()
        self.crypto = WalletCrypto()
        self.network = WalletNetwork()
        self.spv_monitor = SPVMonitor(self.network)
        self.transaction_builder = TransactionBuilder(self.crypto)
        self.scanner = WalletScanner(self.crypto, self.network)
        self.ui = WalletUI(self)
        
        # Variables d'état
        self.initialized = False
        self.satoshis_per_bsv = 100000000
        
        # Initialiser le SPV complet (sera configuré après l'init crypto)
        self.true_spv = None
        
        # Initialiser le module Paymail (sera configuré après l'init)
        self.paymail = None

        # =================================================================
        # NOUVEAU: Attributs pour la gestion du cache de la balance
        # =================================================================
        self.cached_addresses_with_funds = []
        self.cached_balance = 0
        self.cached_balance_timestamp = None # Pour savoir quand le cache a été mis à jour
        # =================================================================

    def initialize(self):
        """Initialise le portefeuille complet avec support Paymail."""
        print("🚀 --- BSV Wallet v4.0 - Multi-Address avec Menu, SPV et Paymail ---")
        
        if not self.config.read_config():
            print("❌ Impossible de lire la configuration.")
            if self.config.create_default_config():
                print("📝 Fichier config.ini créé. Configurez-le et relancez le programme.")
            return False
        
        wallet_config = self.config.get_wallet_config()
        self.crypto.set_derivation_path(wallet_config['derivation_path'])
        self.scanner.scan_depth = wallet_config['scan_depth']
        
        is_valid, error_msg = self.config.validate_mnemonic()
        if not is_valid:
            self.ui.show_startup_error(error_msg)
            return False
        
        mnemonic, passcode = self.config.get_mnemonic()
        success, error_msg = self.crypto.initialize_from_mnemonic(mnemonic, passcode)
        if not success:
            self.ui.show_startup_error(error_msg)
            return False
        
        print("✅ Portefeuille initialisé avec succès!")
        
        try:
            self.true_spv = TrueSPVClient(self.network)
            print("✅ Module SPV complet activé!")
        except Exception as e:
            print(f"⚠️  Module SPV complet non disponible: {e}")
        
        try:
            self.paymail = PaymailIntegration(self)
            print("✅ Module Paymail activé!")
        except Exception as e:
            print(f"⚠️  Module Paymail non disponible: {e}")
        
        self.initialized = True
        return True
    
    # =================================================================
    # NOUVEAU: Méthode pour obtenir la balance (avec gestion de cache)
    # =================================================================
    def get_balance(self, force_refresh=False):
        """
        Récupère la balance, depuis le cache ou via un nouveau scan.
        Met à jour le cache si un nouveau scan est effectué.
        Retourne (adresses_avec_fonds, balance_totale, timestamp_du_cache)
        """
        # Si on force le rafraîchissement ou si le cache est vide, on scanne
        if force_refresh or not self.cached_balance_timestamp:
            if force_refresh:
                print("🔄 Rafraîchissement forcé de la balance...")
            else:
                print("💰 Le cache de la balance est vide, premier scan en cours...")

            try:
                addresses, total_balance = self.scanner.scan_all_addresses()
                # Mettre à jour le cache
                self.cached_addresses_with_funds = addresses
                self.cached_balance = total_balance
                self.cached_balance_timestamp = datetime.now()
                print("✅ Cache de la balance mis à jour.")
            except Exception as e:
                print(f"❌ Erreur lors du scan: {e}")
                # En cas d'erreur, on retourne les anciennes données du cache pour ne pas tout perdre
                return self.cached_addresses_with_funds, self.cached_balance, self.cached_balance_timestamp
        else:
            print("💰 Utilisation de la balance depuis le cache.")

        return self.cached_addresses_with_funds, self.cached_balance, self.cached_balance_timestamp

    def send_funds(self, tx_config):
        """Envoie des fonds en utilisant la configuration fournie."""
        print("-" * 60)
        print("MODE TRANSFERT DE FONDS v4.0")
        print("-" * 60)
        
        dest_address = tx_config['destination_address']
        amount_bsv = tx_config['amount_bsv']
        fee_per_byte = tx_config['fee_per_byte']
        amount_sats = int(amount_bsv * self.satoshis_per_bsv)
        
        final_address = dest_address
        is_paymail = False
        paymail_info = {}
        
        if self.paymail and self.paymail.paymail_client.is_paymail_address(dest_address):
            print(f"📧 Adresse Paymail détectée: {dest_address}, résolution en cours...")
            resolution = self.paymail.resolve_destination(dest_address, amount_bsv)
            if resolution['success']:
                final_address = resolution.get('address') or resolution.get('output') # Gère les deux cas
                if not self.crypto.validate_address(final_address): # Si c'est un script, on ne peut pas l'utiliser directement
                     print(f"❌ Erreur: La résolution Paymail a retourné un script qui n'a pas pu être converti en adresse valide.")
                     return False
                is_paymail = True
                paymail_info = resolution
            else:
                print(f"❌ Erreur résolution Paymail: {resolution['error']}")
                return False
        
        print(f"🎯 OBJECTIF:")
        print(f"   🔗 Destination: {final_address}")
        
        # MODIFICATION: Forcer le rafraîchissement avant un envoi est crucial
        print("\n🔍 Vérification des fonds disponibles (scan complet)...")
        addresses_with_funds, total_balance, _ = self.get_balance(force_refresh=True)
        
        if not addresses_with_funds:
            print("❌ Aucune adresse avec des fonds trouvée.")
            return False
        
        if total_balance < amount_sats:
            print(f"❌ Fonds insuffisants.")
            return False
        
        selected_utxos, selected_total, estimated_fee = self.transaction_builder.select_utxos_for_amount(
            addresses_with_funds, amount_sats, fee_per_byte
        )
        
        if not selected_utxos:
            print("❌ Impossible de sélectionner des UTXOs appropriés.")
            return False
        
        change_sats = selected_total - amount_sats - estimated_fee
        change_address = addresses_with_funds[0]['address']
        
        tx_summary = {
            'destination': final_address, 'amount': Decimal(amount_sats) / self.satoshis_per_bsv,
            'fee': Decimal(estimated_fee) / self.satoshis_per_bsv, 'change': Decimal(change_sats) / self.satoshis_per_bsv,
            'utxo_count': len(selected_utxos), 'address_count': len(set(u['address'] for u in selected_utxos)),
            'is_paymail': is_paymail, 'paymail_address': dest_address,
            'paymail_memo': paymail_info.get('memo'), 'paymail_reference': paymail_info.get('reference')
        }
        
        if not self.ui.confirm_transaction(tx_summary):
            print("Transaction annulée.")
            return False

        print("\n🔨 Création et signature de la transaction...")
        outputs = [{'address': final_address, 'value': amount_sats}]
        if change_sats > 546:
            outputs.append({'address': change_address, 'value': change_sats})
        
        try:
            raw_tx_hex = self.transaction_builder.create_multi_address_transaction(selected_utxos, outputs, change_address)
            if not raw_tx_hex:
                print("❌ ERREUR: Impossible de créer la transaction.")
                return False

            self._save_transaction(raw_tx_hex, is_paymail, paymail_info if is_paymail else None)
            
            if self.ui.confirm_broadcast():
                print("📡 Diffusion de la transaction sur le réseau...")
                tx_id = self.network.broadcast_transaction(raw_tx_hex)
                if tx_id:
                    print(f"\n🎉 >> TRANSACTION ENVOYÉE AVEC SUCCÈS ! <<")
                    print(f"   🆔 ID de la Transaction (TxID): {tx_id}")
                    return True
                else:
                    print("❌ ERREUR: La diffusion de la transaction a échoué.")
                    return False
            else:
                print("💾 Transaction créée mais non diffusée.")
                return True
                
        except Exception as e:
            print(f"❌ ERREUR lors de la création de la transaction: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def monitor_address_spv(self, address, expected_amount=None, use_merkle_proofs=False):
        """Lance la surveillance SPV d'une adresse."""
        scripthash = self.crypto.address_to_scripthash(address)
        if not scripthash:
            print("❌ Erreur: Impossible de convertir l'adresse pour la surveillance")
            return False
        
        spv_config = self.config.get_spv_config()
        
        try:
            if use_merkle_proofs and self.true_spv:
                self.true_spv.monitor_address_with_proofs(address, scripthash, expected_amount)
            else:
                self.spv_monitor.monitor_address(
                    address, scripthash, expected_amount, 
                    spv_config['check_interval'], spv_config['show_periodic_checks']
                )
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la surveillance SPV: {e}")
            return False
    
    def _save_transaction(self, raw_tx_hex, is_paymail=False, paymail_info=None):
        """Sauvegarde une transaction dans un fichier avec métadonnées."""
        try:
            os.makedirs('transactions', exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'transactions/tx_{timestamp}.hex'
            
            with open(filename, 'w') as f:
                f.write(f"# BSV Wallet v4.0 Transaction\n")
                if is_paymail and paymail_info:
                    f.write(f"# Paymail: {paymail_info.get('original_paymail')}\n")
                f.write(raw_tx_hex)
            
            print(f"💾 Transaction sauvegardée dans '{filename}'")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
            return False
    
    def run(self):
        """Lance le portefeuille avec le menu principal."""
        if not self.initialize():
            return
        self.ui.show_main_menu()

def main():
    """Point d'entrée principal du programme."""
    try:
        wallet_manager = BSVWalletManager()
        wallet_manager.run()
    except KeyboardInterrupt:
        print("\n\n👋 Programme interrompu par l'utilisateur")
    except Exception as e:
        print(f"❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
