"""
balance_ui.py
=============
Interface utilisateur pour la gestion de la balance (Phase 3)

Responsabilités:
- Afficher la balance totale et détaillée du portefeuille.
- Interagir avec le WalletManager pour obtenir la balance (depuis le cache ou non).
- Proposer une option pour forcer le rafraîchissement.
"""

from decimal import Decimal

class BalanceUI:
    """Interface utilisateur dédiée à l'affichage de la balance."""
    
    def __init__(self, wallet_manager):
        self.wallet_manager = wallet_manager
        self.wallet = wallet_manager

    def show_balance_menu(self):
        """Menu principal pour vérifier la balance, avec gestion de cache."""
        # La première fois qu'on entre, on fait un scan si le cache est vide
        self.wallet_manager.get_balance(force_refresh=False)

        while True:
            print("\n" + "="*60)
            print("💰 VÉRIFICATION DE LA BALANCE")
            print("="*60)
            
            # Récupérer les données directement depuis les attributs du cache
            addresses_with_funds = self.wallet_manager.cached_addresses_with_funds
            total_balance = self.wallet_manager.cached_balance
            timestamp = self.wallet_manager.cached_balance_timestamp
            
            helpers = getattr(self.wallet_manager.ui, 'helpers', None)
            
            if helpers:
                # Utilise une version modifiée de format_balance_summary qui n'affiche plus le message "Utilisez l'option..."
                display_text = self._format_balance_summary_custom(helpers, addresses_with_funds, total_balance)
            else:
                # Logique de fallback
                if not addresses_with_funds:
                    display_text = "💰 Aucun solde trouvé."
                else:
                    total_bsv = Decimal(total_balance) / self.wallet.satoshis_per_bsv
                    display_text = f"🎉 TOTAL DISPONIBLE: {total_bsv:.8f} BSV ({total_balance} satoshis)"

            print(f"\n{display_text}")
            
            if timestamp:
                print(f"   (Données en cache du {timestamp.strftime('%Y-%m-%d %H:%M:%S')})")
            else:
                print("   (Aucune donnée en cache, un rafraîchissement est nécessaire)")


            print("\nOptions:")
            print("  1. 🔄 Rafraîchir la balance (nouveau scan)")
            print("  2. 📊 Voir le détail des adresses")
            print("  3. 🚪 Retour au menu principal")
            
            choice = input("\nVotre choix (1-3): ").strip()

            if choice == '1':
                # On appelle la méthode en forçant le rafraîchissement.
                # La boucle se relancera et affichera la nouvelle balance.
                self.wallet_manager.get_balance(force_refresh=True)
            elif choice == '2':
                self._show_detailed_balance()
            elif choice == '3':
                break
            else:
                print("❌ Choix invalide.")

    def _show_detailed_balance(self):
        """Affiche le détail de chaque adresse contenant des fonds."""
        print("\n" + "-"*60)
        print("📊 DÉTAIL DES ADRESSES AVEC FONDS")
        print("-"*60)

        addresses_with_funds = self.wallet_manager.cached_addresses_with_funds
        helpers = getattr(self.wallet_manager.ui, 'helpers', None)

        if not addresses_with_funds:
            print("Aucune adresse avec des fonds trouvée dans le cache.")
            print("Essayez de rafraîchir la balance d'abord.")
        else:
            for addr_info in addresses_with_funds:
                address = addr_info.get('address', 'Adresse inconnue')
                balance = addr_info.get('balance', 0)
                index = addr_info.get('index', '?')

                balance_display = f"{Decimal(balance) / self.wallet.satoshis_per_bsv:.8f} BSV"
                if helpers:
                    balance_display = helpers.format_bsv_amount(balance, show_satoshis=False)

                print(f"  • Idx {index}: {address}  ({balance_display})")
        
        input("\nAppuyez sur Entrée pour revenir...")

    def _format_balance_summary_custom(self, helpers, addresses_with_funds, total_balance):
        """Formate un résumé de balance sans le message d'aide redondant."""
        if not addresses_with_funds:
            return "💰 Aucun solde trouvé sur les adresses scannées."
        
        lines = []
        lines.append(f"🎉 TOTAL DISPONIBLE: {helpers.format_bsv_amount(total_balance)}")
        
        address_count = len(addresses_with_funds)
        if address_count > 0:
            plural = "adresses" if address_count > 1 else "adresse"
            lines.append(f"   Réparti sur {address_count} {plural}")
        
        return "\n".join(lines)
