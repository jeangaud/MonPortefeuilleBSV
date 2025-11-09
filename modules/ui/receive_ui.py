"""
receive_ui.py
=============
Interface utilisateur pour la réception de fonds (Phase 3)

Responsabilités:
- Gérer le menu de réception de fonds.
- Permettre à l'utilisateur de choisir une adresse de réception.
- Lancer la surveillance SPV (simple ou complète) pour une adresse.
"""

from decimal import Decimal

class ReceiveUI:
    """Interface utilisateur dédiée à la réception de fonds."""

    def __init__(self, wallet_manager):
        # On stocke le manager principal pour accéder à tous les modules
        self.wallet_manager = wallet_manager
        # Raccourci pratique
        self.wallet = wallet_manager

    def show_receive_menu(self):
        """Menu pour recevoir des fonds avec mode SPV."""
        print("\n" + "="*60)
        print("📥 RÉCEPTION DE FONDS - MODE SPV")
        print("="*60)
        
        address, path = self._select_receiving_address()
        if not address:
            input("\nAppuyez sur Entrée pour revenir au menu...")
            return

        print(f"\n📍 Adresse de réception sélectionnée:")
        print(f"   {address}")
        if path != "Manuel":
            print(f"   Chemin de dérivation: {path}")
        
        self._show_current_balance(address)
        
        print(f"\n📱 Partagez cette adresse pour recevoir des BSV.")
        
        expected_amount = self._get_expected_amount()
        
        use_merkle_proofs = self._select_spv_mode()
        
        print(f"\n🔄 Démarrage de la surveillance SPV...")
        try:
            self.wallet.monitor_address_spv(address, expected_amount, use_merkle_proofs)
        except Exception as e:
            print(f"❌ Erreur lors du lancement de la surveillance: {e}")
        
        input("\nAppuyez sur Entrée pour revenir au menu...")

    def _select_receiving_address(self):
        """Permet à l'utilisateur de choisir une adresse de réception."""
        print("Choix de l'adresse de réception:")
        print("  1. Utiliser l'adresse 0 (première adresse du portefeuille)")
        print("  2. Choisir un index d'adresse spécifique")
        print("  3. Entrer une adresse manuellement pour la surveiller")
        
        choice = input("\nVotre choix (1-3): ").strip()
        
        if choice == '1':
            addr_info = self.wallet.crypto.get_address_info(0)
            return (addr_info['address'], addr_info['path']) if addr_info else (None, None)
        
        elif choice == '2':
            try:
                index_str = input(f"Index de l'adresse (0-{self.wallet.scanner.scan_depth-1}): ")
                index = int(index_str)
                if 0 <= index < self.wallet.scanner.scan_depth:
                    addr_info = self.wallet.crypto.get_address_info(index)
                    return (addr_info['address'], addr_info['path']) if addr_info else (None, None)
                else:
                    print(f"❌ Index invalide.")
                    return None, None
            except (ValueError, TypeError):
                print("❌ Index invalide. Veuillez entrer un nombre.")
                return None, None

        elif choice == '3':
            address = input("Entrez l'adresse à surveiller: ").strip()
            if not self.wallet.crypto.validate_address(address):
                print("❌ Adresse invalide.")
                return None, None
            return address, "Manuel"
            
        else:
            print("❌ Choix invalide.")
            return None, None

    def _show_current_balance(self, address):
        """Affiche le solde actuel d'une adresse."""
        has_funds, current_balance = self.wallet.scanner.check_address_has_funds(address)
        if has_funds:
            # CORRECTION: On récupère les helpers au moment de l'utilisation.
            helpers = getattr(self.wallet_manager.ui, 'helpers', None)
            balance_display = f"{Decimal(current_balance) / self.wallet.satoshis_per_bsv:.8f} BSV"
            if helpers:
                balance_display = helpers.format_bsv_amount(current_balance, False)
            print(f"   Solde actuel: {balance_display}")

    def _get_expected_amount(self):
        """Demande à l'utilisateur un montant attendu (optionnel)."""
        expected_str = input("\nMontant attendu en BSV (optionnel, Entrée pour ignorer): ").strip()
        if not expected_str:
            return None
        
        try:
            amount = Decimal(expected_str)
            if amount <= 0:
                print("❌ Le montant doit être positif.")
                return None
            return amount
        except Exception:
            print("❌ Montant invalide.")
            return None

    def _select_spv_mode(self):
        """Permet à l'utilisateur de choisir le type de surveillance SPV."""
        print(f"\n🔍 TYPE DE SURVEILLANCE SPV:")
        print(f"  1. 📊 Surveillance simple (rapide, fait confiance au serveur)")
        print(f"  2. 🔐 Surveillance complète avec preuves Merkle (sécurisé)")
        
        spv_choice = input("\nVotre choix (1-2): ").strip()
        
        if spv_choice == '2':
            print(f"\n🔐 Mode SPV complet sélectionné - Vérification cryptographique activée.")
            return True
        
        print(f"\n📊 Mode SPV simple sélectionné par défaut.")
        return False
