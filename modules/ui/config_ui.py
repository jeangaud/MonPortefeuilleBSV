"""
config_ui.py
============
Interface utilisateur Configuration pour BSV Wallet v4.0

Responsabilités:
- Menu principal de configuration
- Modification d'adresses de destination (Bitcoin/Paymail)
- Modification des montants et frais
- Aide et documentation
- Validation des entrées utilisateur

Extrait de wallet_ui.py pour améliorer la modularité.
"""

class ConfigUI:
    """Interface utilisateur dédiée à la configuration du portefeuille."""
    
    def __init__(self, wallet_manager):
        self.wallet = wallet_manager
        self.satoshis_per_bsv = 100000000
    
    def show_config_menu(self):
        """Menu principal de configuration."""
        while True:
            print("\n" + "="*60)
            print("⚙️ CONFIGURATION")
            print("="*60)
            
            status = self.wallet.config.get_config_status()
            
            if status.get('status') == 'error':
                print(f"❌ {status['message']}")
            else:
                print("Configuration actuelle:")
                
                # Mnémonique
                mnemonic_info = status.get('mnemonic', {})
                if mnemonic_info.get('configured'):
                    word_count = mnemonic_info.get('word_count', 0)
                    valid = mnemonic_info.get('valid', False)
                    status_emoji = "✅" if valid else "⚠️"
                    print(f"   Mnémonique: {status_emoji} Configurée ({word_count} mots)")
                    if not valid:
                        print(f"      ⚠️  ATTENTION: {word_count} mots trouvés, 12 requis!")
                else:
                    print(f"   Mnémonique: ❌ NON CONFIGURÉE")
                
                # Configuration de transaction
                tx_info = status.get('transaction', {})
                if tx_info:
                    dest_status = "✅" if tx_info.get('destination_configured') else "❌"
                    dest_addr = tx_info.get('destination_address', 'NON CONFIGURÉE')
                    
                    # Déterminer le type d'adresse
                    addr_type = ""
                    if hasattr(self.wallet, 'paymail') and self.wallet.paymail and dest_addr != 'NON CONFIGURÉE':
                        if self.wallet.paymail.paymail_client.is_paymail_address(dest_addr):
                            addr_type = " (📧 Paymail)"
                        else:
                            addr_type = " (🔗 Bitcoin)"
                    
                    print(f"   Adresse destination: {dest_status} {dest_addr}{addr_type}")
                    print(f"   Montant à envoyer: {tx_info.get('amount', 'NON CONFIGURÉ')} BSV")
                    print(f"   Frais par byte: {tx_info.get('fee_per_byte', 'NON CONFIGURÉ')} sat/byte")
                
                # Configuration du portefeuille
                wallet_info = status.get('wallet', {})
                if wallet_info:
                    print(f"   Chemin de dérivation: {wallet_info.get('derivation_path', 'NON CONFIGURÉ')}")
                    print(f"   Profondeur de scan: {wallet_info.get('scan_depth', 'NON CONFIGURÉ')} adresses")
                
                # Status Paymail
                if hasattr(self.wallet, 'paymail') and self.wallet.paymail:
                    print(f"   📧 Support Paymail: ✅ Activé (Module UI)")
                else:
                    print(f"   📧 Support Paymail: ❌ Non disponible")
            
            print(f"\nOptions:")
            print(f"   1. Modifier l'adresse de destination (Bitcoin/Paymail)")
            print(f"   2. Modifier le montant de transaction")
            print(f"   3. Modifier les frais par byte")
            print(f"   4. Modifier le chemin de dérivation")
            print(f"   5. Modifier la profondeur de scan")
            print(f"   6. Voir l'aide de configuration")
            print(f"   7. Retour au menu principal")
            
            choice = input("\nVotre choix (1-7): ").strip()
            
            if choice == '1':
                self.modify_destination_address()
            elif choice == '2':
                self.modify_amount()
            elif choice == '3':
                self.modify_fee()
            elif choice == '4':
                self.modify_derivation_path()
            elif choice == '5':
                self.modify_scan_depth()
            elif choice == '6':
                self.show_configuration_help()
            elif choice == '7':
                break
            else:
                print("❌ Choix invalide. Veuillez choisir entre 1 et 7.")
        
        input("\nAppuyez sur Entrée pour revenir au menu...")
    
    def modify_destination_address(self):
        """Modifie l'adresse de destination avec support Paymail."""
        print(f"\n📍 MODIFICATION DE L'ADRESSE DE DESTINATION")
        print(f"-" * 50)
        
        current_config = self.wallet.config.get_transaction_config()
        if current_config:
            current_addr = current_config['destination_address']
            print(f"Adresse actuelle: {current_addr}")
            
            # Détecter le type actuel
            if hasattr(self.wallet, 'paymail') and self.wallet.paymail:
                if self.wallet.paymail.paymail_client.is_paymail_address(current_addr):
                    print(f"Type actuel: 📧 Paymail")
                else:
                    print(f"Type actuel: 🔗 Bitcoin classique")
        
        print(f"\nTypes d'adresses supportées:")
        if hasattr(self.wallet, 'paymail') and self.wallet.paymail:
            print(f"  1. 📧 Adresse Paymail (ex: alice@handcash.io)")
        print(f"  2. 🔗 Adresse Bitcoin classique (ex: 1ABC...xyz)")
        
        print(f"\nEntrez la nouvelle adresse de destination:")
        print(f"(Laissez vide pour annuler)")
        
        new_address = input("Nouvelle adresse: ").strip()
        
        if not new_address:
            print("❌ Modification annulée")
            return False
        
        # Vérifier le type d'adresse
        if hasattr(self.wallet, 'paymail') and self.wallet.paymail and self.wallet.paymail.paymail_client.is_paymail_address(new_address):
            # C'est une adresse Paymail
            print(f"\n📧 Adresse Paymail détectée: {new_address}")
            print(f"🔍 Vérification de la validité...")
            
            # Tester la résolution Paymail
            info = self.wallet.paymail.paymail_client.get_paymail_info(new_address)
            
            if info['success']:
                print(f"✅ Paymail valide!")
                print(f"   Domaine: {info['domain']}")
                print(f"   Fonctionnalités: {', '.join(info['supported_features'])}")
            else:
                print(f"❌ Erreur Paymail: {info['error']}")
                retry = input("Utiliser quand même cette adresse? (o/n): ").lower()
                if retry != 'o':
                    return False
        
        elif self.wallet.crypto.validate_address(new_address):
            # C'est une adresse Bitcoin classique
            print(f"\n🔗 Adresse Bitcoin classique détectée")
        
        else:
            print("❌ Adresse invalide. L'adresse doit être soit:")
            if hasattr(self.wallet, 'paymail') and self.wallet.paymail:
                print("  • Une adresse Paymail valide (alias@domain.com)")
            print("  • Une adresse Bitcoin valide (1ABC...xyz)")
            return False
        
        # Demander confirmation
        print(f"\n📍 Nouvelle adresse: {new_address}")
        confirm = input("Confirmer cette adresse? (o/n): ").lower()
        
        if confirm != 'o':
            print("❌ Modification annulée")
            return False
        
        # Sauvegarder dans config.ini
        success, message = self.wallet.config.update_destination_address(new_address)
        
        if success:
            print(f"✅ {message}")
            print(f"💾 Configuration sauvegardée dans config.ini")
            return True
        else:
            print(f"❌ {message}")
            return False

    def modify_derivation_path(self):
        """Modifie le chemin de dérivation BIP32."""
        print(f"\n🛤️ MODIFICATION DU CHEMIN DE DÉRIVATION")
        print(f"-" * 50)
        
        wallet_config = self.wallet.config.get_wallet_config()
        current_path = wallet_config['derivation_path']
        
        print(f"Chemin actuel: {current_path}")
        
        print(f"\nChemins de dérivation courants:")
        print(f"   m/44'/0'/0'   = Bitcoin Legacy (Standard)")
        print(f"   m/44'/236'/0' = Bitcoin SV officiel (Coin type 236)")
        print(f"   m/49'/0'/0'   = Bitcoin SegWit P2SH")
        print(f"   m/84'/0'/0'   = Bitcoin Native SegWit")
        
        print(f"\nEntrez le nouveau chemin de dérivation:")
        print(f"Format: m/purpose'/coin_type'/account' (avec apostrophes pour hardened)")
        print(f"(Laissez vide pour annuler)")
        
        new_path = input("Nouveau chemin: ").strip()
        
        if not new_path:
            print("❌ Modification annulée")
            return False
        
        # Demander confirmation
        print(f"\n🛤️ Nouveau chemin: {new_path}")
        print(f"⚠️  ATTENTION: Changer le chemin de dérivation donnera accès à des adresses différentes!")
        print(f"   Assurez-vous de sauvegarder l'ancien chemin si vous avez des fonds dessus.")
        
        confirm = input("Confirmer ce changement? (oui/non): ").lower()
        
        if confirm != 'oui':
            print("❌ Modification annulée")
            return False
        
        # Sauvegarder dans config.ini
        success, message = self.wallet.config.update_derivation_path(new_path)
        
        if success:
            print(f"✅ {message}")
            print(f"💾 Configuration sauvegardée dans config.ini")
            print(f"🔄 Redémarrez le portefeuille pour appliquer les changements")
            return True
        else:
            print(f"❌ {message}")
            return False
    
    def modify_scan_depth(self):
        """Modifie la profondeur de scan des adresses."""
        print(f"\n🔍 MODIFICATION DE LA PROFONDEUR DE SCAN")
        print(f"-" * 50)
        
        wallet_config = self.wallet.config.get_wallet_config()
        current_depth = wallet_config['scan_depth']
        
        print(f"Profondeur actuelle: {current_depth} adresses")
        
        print(f"\nRecommandations:")
        print(f"   10-20   = Utilisation normale")
        print(f"   50-100  = Portefeuille très utilisé")
        print(f"   200+    = Récupération complète (plus lent)")
        
        print(f"\nEntrez la nouvelle profondeur de scan:")
        print(f"(Nombre d'adresses à vérifier lors du scan)")
        print(f"(Laissez vide pour annuler)")
        
        depth_str = input("Nouvelle profondeur (1-1000): ").strip()
        
        if not depth_str:
            print("❌ Modification annulée")
            return False
        
        try:
            new_depth = int(depth_str)
            if new_depth < 1 or new_depth > 1000:
                print("❌ La profondeur doit être entre 1 et 1000")
                return False
        except ValueError:
            print("❌ Veuillez entrer un nombre entier")
            return False
        
        # Demander confirmation
        print(f"\n🔍 Nouvelle profondeur: {new_depth} adresses")
        if new_depth > current_depth:
            print(f"   ℹ️ Scan plus approfondi (plus lent mais plus complet)")
        elif new_depth < current_depth:
            print(f"   ℹ️ Scan plus rapide (moins d'adresses vérifiées)")
        
        confirm = input("Confirmer cette profondeur? (o/n): ").lower()
        
        if confirm != 'o':
            print("❌ Modification annulée")
            return False
        
        # Sauvegarder dans config.ini
        success, message = self.wallet.config.update_scan_depth(new_depth)
        
        if success:
            print(f"✅ {message}")
            print(f"💾 Configuration sauvegardée dans config.ini")
            print(f"🔄 Redémarrez le portefeuille pour appliquer les changements")
            return True
        else:
            print(f"❌ {message}")
            return False

    def modify_amount(self):
        """Modifie le montant à envoyer."""
        print(f"\n💰 MODIFICATION DU MONTANT")
        print(f"-" * 50)
        
        current_config = self.wallet.config.get_transaction_config()
        if current_config:
            print(f"Montant actuel: {current_config['amount_bsv']:.8f} BSV")
        
        print(f"\nEntrez le nouveau montant en BSV:")
        print(f"(Exemple: 0.001 pour 1000 satoshis)")
        print(f"(Laissez vide pour annuler)")
        
        amount_str = input("Nouveau montant (BSV): ").strip()
        
        if not amount_str:
            print("❌ Modification annulée")
            return False
        
        try:
            new_amount = float(amount_str)
            if new_amount <= 0:
                print("❌ Le montant doit être positif")
                return False
            if new_amount < 0.00000546:  # Dust limit
                print("❌ Le montant est trop petit (dust limit: 546 satoshis)")
                return False
        except ValueError:
            print("❌ Montant invalide. Utilisez un nombre décimal (ex: 0.001)")
            return False
        
        # Demander confirmation
        print(f"\n💰 Nouveau montant: {new_amount:.8f} BSV ({int(new_amount * self.satoshis_per_bsv)} satoshis)")
        confirm = input("Confirmer ce montant? (o/n): ").lower()
        
        if confirm != 'o':
            print("❌ Modification annulée")
            return False
        
        # Sauvegarder dans config.ini
        success, message = self.wallet.config.update_transaction_amount(new_amount)
        
        if success:
            print(f"✅ {message}")
            print(f"💾 Configuration sauvegardée dans config.ini")
            return True
        else:
            print(f"❌ {message}")
            return False

    def modify_fee(self):
        """Modifie les frais par byte."""
        print(f"\n⚡ MODIFICATION DES FRAIS")
        print(f"-" * 50)
        
        current_config = self.wallet.config.get_transaction_config()
        if current_config:
            print(f"Frais actuels: {current_config['fee_per_byte']} sat/byte")
        
        print(f"\nEntrez les nouveaux frais en satoshis par byte:")
        print(f"Recommandations:")
        print(f"  • 1 sat/byte = Standard (lent)")
        print(f"  • 2-5 sat/byte = Rapide")
        print(f"  • 10+ sat/byte = Très rapide")
        print(f"(Laissez vide pour annuler)")
        
        fee_str = input("Nouveaux frais (sat/byte): ").strip()
        
        if not fee_str:
            print("❌ Modification annulée")
            return False
        
        try:
            new_fee = int(fee_str)
            if new_fee <= 0:
                print("❌ Les frais doivent être positifs")
                return False
            if new_fee > 1000:
                print("⚠️  Frais très élevés! Êtes-vous sûr?")
                confirm_high = input("Continuer avec des frais élevés? (o/n): ").lower()
                if confirm_high != 'o':
                    return False
        except ValueError:
            print("❌ Frais invalides. Utilisez un nombre entier (ex: 2)")
            return False
        
        # Demander confirmation
        print(f"\n⚡ Nouveaux frais: {new_fee} sat/byte")
        if new_fee == 1:
            print("   (Transaction standard - peut prendre du temps)")
        elif new_fee <= 5:
            print("   (Transaction rapide)")
        else:
            print("   (Transaction très rapide)")
        
        confirm = input("Confirmer ces frais? (o/n): ").lower()
        
        if confirm != 'o':
            print("❌ Modification annulée")
            return False
        
        # Sauvegarder dans config.ini
        success, message = self.wallet.config.update_fee_per_byte(new_fee)
        
        if success:
            print(f"✅ {message}")
            print(f"💾 Configuration sauvegardée dans config.ini")
            return True
        else:
            print(f"❌ {message}")
            return False

    def show_configuration_help(self):
        """Affiche l'aide de configuration avec informations Paymail."""
        print("\n" + "="*60)
        print("📖 AIDE DE CONFIGURATION")
        print("="*60)
        
        print("📝 Instructions de configuration manuelle:")
        print("   1. Ouvrez config.ini dans un éditeur de texte")
        print("   2. Remplacez 'your twelve word...' par votre vraie mnémonique de 12 mots")
        print("   3. Configurez les paramètres de transaction si nécessaire")
        print("   4. Sauvegardez et redémarrez le programme")
        
        print(f"\n💡 Exemple de mnémonique valide:")
        print("   abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about")
        
        print(f"\n📧 SUPPORT PAYMAIL:")
        if hasattr(self.wallet, 'paymail') and self.wallet.paymail:
            print("   ✅ Module Paymail activé")
            print("   • Vous pouvez utiliser des adresses comme alice@handcash.io")
            print("   • Compatible avec HandCash, Relay, Centbee, Money Button")
            print("   • Résolution automatique vers adresses Bitcoin")
            print("   • Interface utilisateur modulaire (PaymailUI)")
        else:
            print("   ❌ Module Paymail non disponible")
            print("   • Assurez-vous que wallet_paymail.py est présent")
            print("   • Vérifiez que modules/ui/paymail_ui.py existe")
            print("   • Redémarrez le portefeuille après avoir ajouté les fichiers")
        
        print(f"\n🏗️ ARCHITECTURE MODULAIRE:")
        print("   ✅ Interface UI modulaire activée")
        print("   • PaymailUI: Interface Paymail complète")
        print("   • ConfigUI: Interface Configuration (ce module)")
        print("   • Architecture extensible pour futures fonctionnalités")
        
        print(f"\n🔗 TYPES D'ADRESSES SUPPORTÉES:")
        print("   • Adresses Bitcoin classiques: 1ABC...xyz")
        if hasattr(self.wallet, 'paymail') and self.wallet.paymail:
            print("   • Adresses Paymail: alias@domain.com")
        
        print(f"\n🛤️ CHEMINS DE DÉRIVATION:")
        print("   • m/44'/0'/0' = Bitcoin Legacy (recommandé)")
        print("   • m/44'/236'/0' = Bitcoin SV officiel")
        print("   • Changement nécessite un redémarrage")
        
        print(f"\n⚠️ SÉCURITÉ:")
        print("   • Gardez votre mnémonique secrète")
        print("   • Ne partagez jamais vos 12 mots")
        print("   • Sauvegardez config.ini en lieu sûr")
        print("   • Testez avec de petits montants d'abord")
        if hasattr(self.wallet, 'paymail') and self.wallet.paymail:
            print("   • Vérifiez les adresses Paymail avant envoi")
        
        input("\nAppuyez sur Entrée pour continuer...")