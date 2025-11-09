"""
paymail_ui.py
=============
Interface utilisateur Paymail pour BSV Wallet v4.0

Responsabilités:
- Menu principal Paymail
- Test d'adresses Paymail
- Informations sur les domaines
- Résolution manuelle d'adresses
- Guide utilisateur Paymail
- Envoi rapide Paymail

Extrait de wallet_ui.py pour améliorer la modularité.
"""

class PaymailUI:
    """Interface utilisateur dédiée aux fonctionnalités Paymail."""
    
    def __init__(self, wallet_manager):
        self.wallet = wallet_manager
        self.satoshis_per_bsv = 100000000
    
    def show_paymail_menu(self):
        """Menu d'informations et de test Paymail."""
        print("\n" + "="*60)
        print("📧 INFORMATIONS PAYMAIL")
        print("="*60)
        
        if not hasattr(self.wallet, 'paymail') or not self.wallet.paymail:
            print("❌ Module Paymail non disponible")
            print("💡 Le support Paymail n'est pas activé dans ce portefeuille")
            print("🔧 Assurez-vous que le fichier wallet_paymail.py est présent")
            input("\nAppuyez sur Entrée pour revenir au menu...")
            return
        
        while True:
            print(f"\nOptions Paymail:")
            print(f"   1. 🔍 Tester une adresse Paymail")
            print(f"   2. 📋 Informations sur un domaine Paymail")
            print(f"   3. 🎯 Résoudre une adresse Paymail")
            print(f"   4. 📚 Guide Paymail")
            print(f"   5. Retour au menu principal")
            
            choice = input("\nVotre choix (1-5): ").strip()
            
            if choice == '1':
                self.test_paymail_address()
            elif choice == '2':
                self.show_domain_info()
            elif choice == '3':
                self.resolve_paymail_address()
            elif choice == '4':
                self.show_paymail_guide()
            elif choice == '5':
                break
            else:
                print("❌ Choix invalide. Veuillez choisir entre 1 et 5.")
        
        input("\nAppuyez sur Entrée pour revenir au menu...")

    def test_paymail_address(self):
        """Teste la validité d'une adresse Paymail."""
        print(f"\n🔍 TEST D'ADRESSE PAYMAIL")
        print(f"-" * 30)
        
        paymail = input("Entrez l'adresse Paymail à tester: ").strip()
        
        if not paymail:
            print("❌ Adresse vide")
            return
        
        # Test du format
        if not self.wallet.paymail.paymail_client.is_paymail_address(paymail):
            print("❌ Format Paymail invalide")
            print("💡 Format attendu: alias@domain.com")
            return
        
        print(f"✅ Format Paymail valide")
        print(f"🔍 Test de connectivité...")
        
        # Test de résolution
        info = self.wallet.paymail.paymail_client.get_paymail_info(paymail)
        
        if info['success']:
            print(f"✅ Serveur Paymail accessible!")
            print(f"📋 Informations:")
            print(f"   • Domaine: {info['domain']}")
            print(f"   • Alias: {info['alias']}")
            print(f"   • Version BSV Alias: {info['bsvalias_version']}")
            print(f"   • Fonctionnalités supportées:")
            for feature in info['supported_features']:
                print(f"     - {feature}")
            
            if not info['supported_features']:
                print(f"     - Aucune fonctionnalité détectée")
        else:
            print(f"❌ Erreur: {info['error']}")
            print(f"💡 Le serveur Paymail peut être indisponible ou ne pas supporter cette adresse")

    def show_domain_info(self):
        """Affiche les informations d'un domaine Paymail avec support HandCash."""
        print(f"\n📋 INFORMATIONS DOMAINE PAYMAIL")
        print(f"-" * 35)
        
        domain = input("Entrez le domaine (ex: handcash.io): ").strip()
        
        if not domain:
            print("❌ Domaine vide")
            return
        
        print(f"🔍 Analyse du domaine {domain}...")
        
        # Cas spécial pour HandCash
        if domain == 'handcash.io':
            print("🔄 HandCash détecté - utilisation des endpoints migrés...")
            handcash_info = self._analyze_handcash_domain()
            if handcash_info:
                return
            # Si HandCash échoue, continuer avec la méthode standard
            print("⚠️  Analyse HandCash échouée, essai méthode standard...")
        
        # Récupérer les capacités du domaine (méthode standard)
        capabilities = self.wallet.paymail.paymail_client._get_paymail_capabilities(domain)
        
        if capabilities['success']:
            print(f"✅ Domaine Paymail actif!")
            print(f"📋 Détails:")
            print(f"   • Version BSV Alias: {capabilities['bsvalias_version']}")
            print(f"   • URL des capacités: https://{domain}/.well-known/bsvalias")
            
            caps = capabilities['capabilities']
            print(f"   • Fonctionnalités supportées:")
            
            features_found = False
            if 'addressResolution' in caps:
                print(f"     ✅ Résolution d'adresse basique")
                features_found = True
            if 'paymentDestination' in caps:
                print(f"     ✅ Destination de paiement P2P")
                features_found = True
            if 'verifyPublicKeyOwner' in caps:
                print(f"     ✅ Vérification de clé publique")
                features_found = True
            if 'publicProfile' in caps:
                print(f"     ✅ Profil public")
                features_found = True
            
            if not features_found:
                print(f"     ⚠️  Aucune fonctionnalité standard détectée")
                print(f"     📋 Capacités brutes: {list(caps.keys())}")
            
            print(f"\n💡 Exemples d'adresses possibles sur ce domaine:")
            print(f"   • alice@{domain}")
            print(f"   • bob@{domain}")
            print(f"   • votrenom@{domain}")
        else:
            print(f"❌ Erreur: {capabilities['error']}")
            print(f"💡 Ce domaine ne supporte pas Paymail ou est indisponible")

    def _analyze_handcash_domain(self):
        """Analyse spéciale pour le domaine HandCash."""
        handcash_endpoints = [
            "https://cloud.handcash.io/.well-known/bsvalias",
            "https://api.handcash.io/.well-known/bsvalias"
        ]
        
        for endpoint in handcash_endpoints:
            try:
                print(f"   📡 Test endpoint: {endpoint}")
                
                import urllib.request
                import json
                
                request = urllib.request.Request(
                    endpoint,
                    headers={
                        'User-Agent': 'BSV-Wallet-v4.0-Paymail-Client',
                        'Accept': 'application/json'
                    }
                )
                
                with urllib.request.urlopen(request, timeout=10) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode('utf-8'))
                        
                        if 'capabilities' in data:
                            print(f"   ✅ Endpoint HandCash fonctionnel!")
                            print(f"✅ Domaine Paymail actif (HandCash migré)!")
                            print(f"📋 Détails:")
                            print(f"   • Version BSV Alias: {data.get('bsvalias', 'Unknown')}")
                            print(f"   • URL des capacités: {endpoint}")
                            print(f"   • Status: Migré vers cloud.handcash.io")
                            
                            caps = data['capabilities']
                            print(f"   • Fonctionnalités supportées:")
                            
                            features_found = False
                            if 'addressResolution' in caps:
                                print(f"     ✅ Résolution d'adresse basique")
                                features_found = True
                            if 'paymentDestination' in caps:
                                print(f"     ✅ Destination de paiement P2P")
                                features_found = True
                            if 'verifyPublicKeyOwner' in caps:
                                print(f"     ✅ Vérification de clé publique")
                                features_found = True
                            if 'publicProfile' in caps:
                                print(f"     ✅ Profil public")
                                features_found = True
                            
                            if not features_found:
                                print(f"     ⚠️  Aucune fonctionnalité standard détectée")
                                print(f"     📋 Capacités brutes: {list(caps.keys())}")
                            
                            print(f"\n📍 IMPORTANT:")
                            print(f"   HandCash a migré son service Paymail")
                            print(f"   Ancien endpoint: handcash.io (❌ Non fonctionnel)")
                            print(f"   Nouvel endpoint: cloud.handcash.io (✅ Fonctionnel)")
                            
                            print(f"\n💡 Exemples d'adresses HandCash:")
                            print(f"   • alice@handcash.io (fonctionne avec ce wallet)")
                            print(f"   • bob@handcash.io")
                            print(f"   • votrenom@handcash.io")
                            
                            return True
            
            except Exception as e:
                print(f"   ❌ {endpoint}: {e}")
                continue
        
        return False

    def resolve_paymail_address(self):
        """Résout une adresse Paymail vers une adresse Bitcoin."""
        print(f"\n🎯 RÉSOLUTION PAYMAIL")
        print(f"-" * 25)
        
        paymail = input("Adresse Paymail: ").strip()
        
        if not paymail:
            print("❌ Adresse vide")
            return
        
        if not self.wallet.paymail.paymail_client.is_paymail_address(paymail):
            print("❌ Format Paymail invalide")
            return
        
        # Demander le montant (optionnel)
        amount_str = input("Montant en BSV (optionnel, pour P2P): ").strip()
        amount_bsv = None
        
        if amount_str:
            try:
                amount_bsv = float(amount_str)
                if amount_bsv <= 0:
                    print("❌ Montant invalide, résolution sans montant")
                    amount_bsv = None
            except ValueError:
                print("❌ Montant invalide, résolution sans montant")
                amount_bsv = None
        
        print(f"🔍 Résolution en cours...")
        
        # Résoudre l'adresse
        result = self.wallet.paymail.resolve_destination(paymail, amount_bsv)
        
        if result['success']:
            print(f"✅ Résolution réussie!")
            print(f"📋 Résultats:")
            print(f"   • Paymail: {paymail}")
            print(f"   • Adresse Bitcoin: {result['address']}")
            
            if result.get('reference'):
                print(f"   • Référence: {result['reference']}")
            if result.get('memo'):
                print(f"   • Memo: {result['memo']}")
            
            if amount_bsv:
                print(f"   • Montant: {amount_bsv:.8f} BSV")
                print(f"   • Type: Résolution P2P avec montant")
            else:
                print(f"   • Type: Résolution d'adresse basique")
            
            # Proposer d'envoyer des fonds
            if amount_bsv:
                send_now = input(f"\nEnvoyer {amount_bsv:.8f} BSV maintenant? (o/n): ").lower()
                if send_now == 'o':
                    try:
                        success = self.wallet.paymail.send_to_paymail(paymail, amount_bsv)
                        if success:
                            print(f"✅ Envoi réussi!")
                        else:
                            print(f"❌ Erreur lors de l'envoi")
                    except Exception as e:
                        print(f"❌ Erreur: {e}")
        else:
            print(f"❌ Échec de la résolution: {result['error']}")

    def show_paymail_guide(self):
        """Affiche le guide Paymail."""
        print(f"\n📚 GUIDE PAYMAIL")
        print(f"=" * 50)
        
        print(f"""
🎯 QU'EST-CE QUE PAYMAIL?

Paymail est un protocole qui permet d'utiliser des adresses 
email-like au lieu des adresses Bitcoin complexes.

📧 EXEMPLES:
   • Au lieu de: 1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2
   • Utilisez: alice@handcash.io

✅ AVANTAGES:
   • Plus facile à retenir et partager
   • Moins d'erreurs de frappe
   • Expérience utilisateur améliorée
   • Compatible avec les standards BSV

🔧 FONCTIONNALITÉS SUPPORTÉES:
   • Résolution d'adresse basique
   • Paiements P2P avec métadonnées
   • Vérification de propriétaire
   • Profils publics (selon le fournisseur)

🏢 FOURNISSEURS POPULAIRES:
   • HandCash (handcash.io)
   • Relay (relysia.com)
   • Centbee (centbee.com)
   • Money Button (moneybutton.com)

💡 UTILISATION DANS CE PORTEFEUILLE:
   1. Dans "Envoyer des BSV", entrez une adresse Paymail
   2. Le portefeuille résoudra automatiquement l'adresse
   3. La transaction sera envoyée normalement

⚠️  IMPORTANT:
   • Vérifiez toujours l'adresse avant d'envoyer
   • Testez avec de petits montants d'abord
   • Certains services peuvent avoir des limitations

🌐 STANDARD:
   Basé sur le protocole bsvalias.org
        """)
        
        input("\nAppuyez sur Entrée pour continuer...")

    def quick_paymail_send(self):
        """Interface d'envoi rapide Paymail."""
        print(f"\n📧 ENVOI RAPIDE PAYMAIL")
        print(f"-" * 30)
        
        if not hasattr(self.wallet, 'paymail') or not self.wallet.paymail:
            print("❌ Module Paymail non disponible")
            print("💡 Le support Paymail n'est pas activé dans ce portefeuille")
            return False
        
        # Demander l'adresse Paymail
        paymail = input("Adresse Paymail de destination: ").strip()
        
        if not paymail:
            print("❌ Adresse vide")
            return False
        
        if not self.wallet.paymail.paymail_client.is_paymail_address(paymail):
            print("❌ Format Paymail invalide (doit être alias@domain.com)")
            return False
        
        # Demander le montant
        amount_str = input("Montant en BSV: ").strip()
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                print("❌ Le montant doit être positif")
                return False
        except ValueError:
            print("❌ Montant invalide")
            return False
        
        # Demander les frais (optionnel)
        fee_str = input("Frais (sat/byte, défaut=1): ").strip()
        fee_per_byte = 1
        
        if fee_str:
            try:
                fee_per_byte = int(fee_str)
                if fee_per_byte <= 0:
                    print("❌ Les frais doivent être positifs")
                    return False
            except ValueError:
                print("❌ Frais invalides, utilisation de 1 sat/byte")
        
        # Afficher le résumé
        print(f"\n📧 RÉSUMÉ ENVOI PAYMAIL:")
        print(f"   Destination: {paymail}")
        print(f"   Montant: {amount:.8f} BSV")
        print(f"   Frais: {fee_per_byte} sat/byte")
        
        confirm = input("\nConfirmer cet envoi Paymail? (oui/non): ").lower()
        
        if confirm == 'oui':
            try:
                success = self.wallet.paymail.send_to_paymail(paymail, amount, fee_per_byte)
                return success
            except Exception as e:
                print(f"❌ Erreur envoi Paymail: {e}")
                return False
        else:
            print("❌ Envoi annulé")
            return False