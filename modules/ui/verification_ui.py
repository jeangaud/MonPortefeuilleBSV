"""
verification_ui.py
==================
Interface utilisateur pour la vérification de transaction (Phase 3)

Responsabilités:
- Gérer le menu de vérification de transaction.
- Demander un TxID à l'utilisateur.
- Interagir avec le module réseau pour obtenir les informations sur la transaction.
- Afficher le statut de confirmation.
"""

class VerificationUI:
    """Interface utilisateur dédiée à la vérification de transaction."""

    def __init__(self, wallet_manager):
        self.wallet = wallet_manager

    def show_verification_menu(self):
        """Menu pour vérifier une transaction BSV."""
        print("\n" + "="*60)
        print("� VÉRIFICATION DE TRANSACTION BSV")
        print("="*60)
        
        print("Vérifiez qu'une transaction est bien incluse dans la blockchain BSV.")
        
        tx_hash = input("\nEntrez le hash de la transaction (TxID): ").strip()
        
        if not self._is_valid_tx_hash(tx_hash):
            input("\nAppuyez sur Entrée pour revenir au menu...")
            return
        
        print(f"\n🔍 Vérification en cours pour le TxID: {tx_hash}")
        
        try:
            # Utiliser le module réseau pour récupérer les informations
            tx_info = self.wallet.network.send_rpc_request("blockchain.transaction.get", [tx_hash, True])
            
            if not tx_info:
                print("\n❌ Transaction introuvable sur le serveur ElectrumX.")
            elif isinstance(tx_info, str):
                print("\n⏳ Transaction trouvée mais pas encore confirmée (en mempool).")
            else:
                confirmations = tx_info.get('confirmations', 0)
                block_height = tx_info.get('block_height') or tx_info.get('height')
                
                if confirmations > 0:
                    print(f"\n✅ TRANSACTION CONFIRMÉE !")
                    print(f"   • Confirmations: {confirmations}")
                    if block_height:
                        print(f"   • Incluse dans le bloc: {block_height}")
                else:
                    print("\n⏳ Transaction trouvée mais avec 0 confirmation.")

            print(f"\n🌐 Lien pour vérification externe: https://whatsonchain.com/tx/{tx_hash}")
        
        except Exception as e:
            print(f"❌ Erreur lors de la communication avec le réseau: {e}")
        
        input("\nAppuyez sur Entrée pour revenir au menu...")

    def _is_valid_tx_hash(self, tx_hash):
        """Valide le format d'un hash de transaction."""
        if not tx_hash:
            print("❌ Le hash de transaction ne peut pas être vide.")
            return False
        
        if len(tx_hash) != 64:
            print("❌ Format de hash invalide (doit contenir 64 caractères).")
            return False
        
        try:
            # Vérifie si la chaîne ne contient que des caractères hexadécimaux
            bytes.fromhex(tx_hash)
            return True
        except ValueError:
            print("❌ Format de hash invalide (contient des caractères non-hexadécimaux).")
            return False
