"""
wallet_ui.py - Version Phase 3 (Routeur Principal)
===================================================
Interface utilisateur principale pour BSV Wallet v4.0

Cette version est entièrement segmentée. Ce module agit comme un simple
"routeur" qui initialise et délègue les tâches aux modules UI spécialisés
contenus dans le package `modules/ui/`.

Responsabilités de cette classe:
- Afficher le menu principal du portefeuille.
- Initialiser et coordonner tous les modules UI.
- Agir comme point d'entrée pour les appels venant du WalletManager
  (ex: confirmations).
"""

from decimal import Decimal

# Import de TOUS les modules UI depuis le package `ui`
# Le fichier __init__.py gère leur disponibilité.
try:
    from modules.ui import (
        UIHelpers,
        ConfigUI,
        PaymailUI,
        BalanceUI,
        SendUI,
        ReceiveUI,
        VerificationUI
    )
except ImportError as e:
    print(f"❌ ERREUR CRITIQUE: Impossible d'importer les modules UI: {e}")
    print("   Vérifiez que tous les fichiers UI sont présents dans 'modules/ui/'")
    print("   et que 'modules/ui/__init__.py' est correctement configuré.")
    # Définir des classes factices pour éviter un crash complet
    UIHelpers = ConfigUI = PaymailUI = BalanceUI = SendUI = ReceiveUI = VerificationUI = None

class WalletUI:
    """Interface utilisateur principale agissant comme un routeur."""
    
    def __init__(self, wallet_manager):
        self.wallet = wallet_manager
        self.satoshis_per_bsv = 100000000
        
        # Initialiser tous les modules UI spécialisés.
        # CORRECTION: On leur passe le wallet_manager principal pour qu'ils aient
        # accès à la fois à la logique (wallet.scanner) et aux autres modules UI
        # (wallet.ui.helpers, wallet.ui.config_ui, etc.).
        self.helpers = UIHelpers() if UIHelpers else None
        self.config_ui = ConfigUI(wallet_manager) if ConfigUI else None
        self.paymail_ui = PaymailUI(wallet_manager) if PaymailUI else None
        self.balance_ui = BalanceUI(wallet_manager) if BalanceUI else None
        self.send_ui = SendUI(wallet_manager) if SendUI else None
        self.receive_ui = ReceiveUI(wallet_manager) if ReceiveUI else None
        self.verification_ui = VerificationUI(wallet_manager) if VerificationUI else None

    def show_main_menu(self):
        """Affiche le menu principal et délègue les tâches."""
        while True:
            print("\n" + "="*60)
            print("🚀 BSV WALLET v4.0 - MENU PRINCIPAL (Phase 3)")
            print("="*60)
            print("1. 💰 Voir la balance")
            print("2. 📤 Envoyer des BSV")
            print("3. 📥 Recevoir des BSV")
            print("4. 🔐 Vérifier une transaction")
            print("5. 📧 Menu Paymail")
            print("6. ⚙️  Configuration")
            print("7. 🚪 Quitter")
            print("="*60)
            
            try:
                choice = input("Votre choix (1-7): ").strip()
                
                if choice == '1' and self.balance_ui:
                    self.balance_ui.show_balance_menu()
                elif choice == '2' and self.send_ui:
                    self.send_ui.show_send_menu()
                elif choice == '3' and self.receive_ui:
                    self.receive_ui.show_receive_menu()
                elif choice == '4' and self.verification_ui:
                    self.verification_ui.show_verification_menu()
                elif choice == '5' and self.paymail_ui:
                    self.paymail_ui.show_paymail_menu()
                elif choice == '6' and self.config_ui:
                    self.config_ui.show_config_menu()
                elif choice == '7':
                    print("\n👋 Au revoir!")
                    break
                else:
                    print("❌ Choix invalide. Veuillez choisir entre 1 et 7.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Au revoir!")
                break
            except Exception as e:
                print(f"❌ Erreur inattendue dans le menu principal: {e}")

    # --- Méthodes de support appelées par WalletManager ---
    # Ces méthodes sont conservées ici car main.py les appelle via self.ui
    
    def show_startup_error(self, error_message):
        """Affiche une erreur de démarrage avec aide."""
        print(f"\n❌ ERREUR DE DÉMARRAGE: {error_message}")
        print("\n💡 AIDE CONFIGURATION:")
        print("1. Vérifiez que le fichier config.ini existe.")
        print("2. Assurez-vous que votre mnémonique contient exactement 12 mots.")
        print("3. Utilisez le menu Configuration pour la modifier si besoin.")
        print("4. Sauvegardez et redémarrez le programme.")

    def confirm_transaction(self, tx_summary):
        """Affiche un résumé de transaction et demande confirmation."""
        if self.helpers:
            formatted_summary = self.helpers.format_transaction_summary(tx_summary)
            print(f"\n{formatted_summary}")
            return self.helpers.confirm_action("Voulez-vous vraiment envoyer cette transaction?", require_yes=True)
        
        # Logique de fallback si les helpers ne sont pas disponibles
        print(f"\n💰 RÉSUMÉ DE LA TRANSACTION:")
        print(f"   🔗 Destination: {tx_summary['destination']}")
        print(f"   💰 Montant: {tx_summary['amount']:.8f} BSV")
        return input("\nVoulez-vous vraiment envoyer cette transaction? (oui/non): ").lower() == 'oui'

    def confirm_broadcast(self):
        """Demande confirmation pour diffuser la transaction."""
        if self.helpers:
            return self.helpers.confirm_action("Diffuser la transaction sur le réseau?", require_yes=True)
        
        return input("\nDiffuser la transaction sur le réseau? (oui/non): ").lower() == 'oui'
