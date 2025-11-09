"""
send_ui.py
==========
Interface utilisateur pour l'envoi de fonds (Phase 3)

Responsabilités:
- Gérer le menu d'envoi de fonds.
- Interagir avec ConfigUI pour modifier la transaction.
- Interagir avec PaymailUI pour les envois rapides.
- Lancer le processus d'envoi via le WalletManager.
"""

class SendUI:
    """Interface utilisateur dédiée à l'envoi de fonds."""

    def __init__(self, wallet_manager):
        # On stocke le manager principal pour accéder à tous les modules
        self.wallet_manager = wallet_manager
        # Raccourci pratique
        self.wallet = wallet_manager

    def show_send_menu(self):
        """Menu pour envoyer des fonds avec support Paymail complet."""
        # CORRECTION: On récupère les autres modules UI ici, au moment de l'utilisation.
        config_ui = getattr(self.wallet_manager.ui, 'config_ui', None)
        paymail_ui = getattr(self.wallet_manager.ui, 'paymail_ui', None)

        while True:
            print("\n" + "="*60)
            print("📤 ENVOI DE FONDS (Bitcoin + Paymail)")
            print("="*60)
            
            tx_config = self.wallet.config.get_transaction_config()
            
            print("Configuration actuelle:")
            if tx_config and tx_config.get('destination_address'):
                dest_addr = tx_config['destination_address']
                is_paymail = self.wallet.paymail.paymail_client.is_paymail_address(dest_addr) if hasattr(self.wallet, 'paymail') else False
                addr_type = "📧 Paymail" if is_paymail else "🔗 Bitcoin"
                print(f"   1. Destination: {dest_addr} ({addr_type})")
                print(f"   2. Montant: {tx_config.get('amount_bsv', 0.0):.8f} BSV")
                print(f"   3. Frais: {tx_config.get('fee_per_byte', 1)} sat/byte")
            else:
                print("   ❌ Configuration de transaction manquante ou incomplète dans config.ini")
                tx_config = {}

            print(f"\nOptions:")
            print(f"   1. ⚙️  Modifier la configuration")
            print(f"   2. 📧 Envoi rapide Paymail")
            print(f"   3. Envoyer avec la configuration ci-dessus")
            print(f"   4. Retour au menu principal")
            
            choice = input("\nVotre choix (1-4): ").strip()
            
            if choice == '1':
                if config_ui:
                    print("🔄 Redirection vers le menu Configuration...")
                    config_ui.show_config_menu()
                else:
                    print("❌ Module ConfigUI non disponible.")
            
            elif choice == '2':
                if paymail_ui and paymail_ui.quick_paymail_send():
                    break 
                elif not paymail_ui:
                    print("❌ Module PaymailUI non disponible.")

            elif choice == '3':
                dest_addr = tx_config.get('destination_address')
                if not dest_addr:
                    print("❌ Adresse de destination non configurée.")
                    input("\nAppuyez sur Entrée pour continuer...")
                    continue

                is_valid_paymail = hasattr(self.wallet, 'paymail') and self.wallet.paymail.paymail_client.is_paymail_address(dest_addr)
                is_valid_btc = self.wallet.crypto.validate_address(dest_addr)

                if is_valid_paymail or is_valid_btc:
                    try:
                        self.wallet.send_funds(tx_config)
                        break 
                    except Exception as e:
                        print(f"❌ Erreur lors de l'envoi: {e}")
                        input("\nAppuyez sur Entrée pour continuer...")
                else:
                    print("❌ Adresse de destination invalide.")
                    input("\nAppuyez sur Entrée pour continuer...")

            elif choice == '4':
                break
            
            else:
                print("❌ Choix invalide.")
        
        print("\nRetour au menu principal...")
