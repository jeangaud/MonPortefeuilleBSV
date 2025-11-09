"""
wallet_config.py - Version corrigée
==================================
Module de gestion de la configuration pour BSV Wallet v4.0

Responsabilités:
- Lecture/écriture du fichier config.ini
- Validation des paramètres
- Création de configuration par défaut
- Gestion des erreurs de configuration
"""

import configparser
import os
from decimal import Decimal

class WalletConfig:
    """Gestionnaire de configuration pour le portefeuille BSV."""
    
    def __init__(self, config_file='config.ini'):
        self.config_file = config_file
        self.config = None
        
    def read_config(self):
        """Lit la configuration depuis le fichier config.ini."""
        if not os.path.exists(self.config_file):
            print(f"\n❌ ERREUR: Fichier '{self.config_file}' introuvable.")
            return False

        self.config = configparser.ConfigParser()
        try:
            self.config.read(self.config_file)
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la lecture de {self.config_file}: {e}")
            return False
    
    def validate_mnemonic(self):
        """Valide la mnémonique de configuration."""
        if not self.config:
            return False, "Configuration non chargée"
            
        try:
            mnemonic = self.config['Credentials']['mnemonic'].strip()
        except KeyError:
            return False, "'mnemonic' manquant dans config.ini"

        # Vérifier que la mnémonique n'est pas vide ou par défaut
        if not mnemonic or mnemonic == "your twelve word mnemonic phrase goes here exactly as given":
            return False, "Mnémonique non configurée - remplacez la valeur par défaut"

        # Vérifier le nombre de mots
        mnemonic_words = mnemonic.split()
        if len(mnemonic_words) != 12:
            return False, f"Mnémonique invalide: {len(mnemonic_words)} mots trouvés, 12 requis"

        return True, "Mnémonique valide"
    
    def get_mnemonic(self):
        """Retourne la mnémonique et le passcode."""
        if not self.config:
            return None, None
            
        try:
            mnemonic = self.config['Credentials']['mnemonic'].strip()
            passcode = self.config['Credentials'].get('passcode', '').strip()
            return mnemonic, passcode
        except KeyError:
            return None, None
    
    def get_transaction_config(self):
        """Retourne la configuration de transaction."""
        if not self.config or not self.config.has_section('Transaction'):
            return None
            
        try:
            return {
                'destination_address': self.config['Transaction']['destination_address'],
                'amount_bsv': Decimal(self.config['Transaction']['amount_to_send_bsv']),
                'fee_per_byte': int(self.config['Transaction'].get('fee_per_byte', 1))
            }
        except (KeyError, ValueError) as e:
            print(f"❌ Erreur dans la configuration de transaction: {e}")
            return None
    
    def get_spv_config(self):
        """Retourne la configuration SPV."""
        if not self.config:
            return {'check_interval': 3, 'show_periodic_checks': True}
            
        try:
            return {
                'check_interval': int(self.config.get('SPV', 'check_interval', fallback=3)),
                'show_periodic_checks': self.config.getboolean('SPV', 'show_periodic_checks', fallback=True)
            }
        except Exception:
            return {'check_interval': 3, 'show_periodic_checks': True}
    
    def get_wallet_config(self):
        """Retourne la configuration du portefeuille."""
        if not self.config:
            return {
                'derivation_path': 'm/44\'/0\'/0\'',
                'scan_depth': 20
            }
            
        try:
            return {
                'derivation_path': self.config.get('Wallet', 'derivation_path', fallback='m/44\'/0\'/0\''),
                'scan_depth': int(self.config.get('Wallet', 'scan_depth', fallback='20'))
            }
        except Exception:
            return {
                'derivation_path': 'm/44\'/0\'/0\'',
                'scan_depth': 20
            }
    
    def get_config_status(self):
        """Retourne le statut de la configuration pour affichage."""
        if not self.config:
            return {"status": "error", "message": "Configuration non chargée"}
        
        status = {}
        
        # Vérifier la mnémonique
        mnemonic = self.config.get('Credentials', 'mnemonic', fallback='')
        mnemonic_words = mnemonic.split() if mnemonic else []
        
        if mnemonic and mnemonic != "your twelve word mnemonic phrase goes here exactly as given":
            status['mnemonic'] = {
                'configured': True, 
                'word_count': len(mnemonic_words),
                'valid': len(mnemonic_words) == 12
            }
        else:
            status['mnemonic'] = {'configured': False, 'word_count': 0, 'valid': False}
        
        # Vérifier le passcode
        passcode = self.config.get('Credentials', 'passcode', fallback='')
        status['passcode'] = {'configured': bool(passcode)}
        
        # Vérifier la configuration du portefeuille
        if self.config.has_section('Wallet'):
            derivation_path = self.config.get('Wallet', 'derivation_path', fallback='m/44\'/0\'/0\'')
            scan_depth = self.config.get('Wallet', 'scan_depth', fallback='20')
            
            status['wallet'] = {
                'derivation_path': derivation_path,
                'scan_depth': scan_depth
            }
        else:
            status['wallet'] = {
                'derivation_path': 'm/44\'/0\'/0\'',
                'scan_depth': '20'
            }
        
        # Vérifier la configuration de transaction
        if self.config.has_section('Transaction'):
            dest_addr = self.config.get('Transaction', 'destination_address', fallback='')
            amount = self.config.get('Transaction', 'amount_to_send_bsv', fallback='')
            fee = self.config.get('Transaction', 'fee_per_byte', fallback='')
            
            status['transaction'] = {
                'destination_configured': dest_addr and dest_addr != '1DestinationAddressGoesHere',
                'destination_address': dest_addr,
                'amount': amount,
                'fee_per_byte': fee
            }
        else:
            status['transaction'] = {'destination_configured': False}
        
        return status
    
    def create_default_config(self):
        """Crée un fichier config.ini par défaut."""
        print("📁 Création d'un fichier config.ini par défaut...")
        
        default_config = """[Credentials]
# Votre phrase mnémonique BIP39 (12 mots)
# IMPORTANT: Gardez cette phrase secrète et sécurisée!
# Remplacez la ligne ci-dessous par votre vraie mnémonique de 12 mots
mnemonic = your twelve word mnemonic phrase goes here exactly as given

# Passcode BIP39 optionnel (laisser vide si aucun)
passcode = 

[Transaction]
# Adresse de destination pour les envois
destination_address = 1DestinationAddressGoesHere

# Montant à envoyer en BSV (ex: 0.001)
amount_to_send_bsv = 0.001

# Frais par byte en satoshis (recommandé: 1-2)
fee_per_byte = 1

[SPV]
# Intervalle de vérification en secondes pour le mode SPV
check_interval = 3

# Afficher les vérifications périodiques (true/false)
show_periodic_checks = true

[Wallet]
# Chemin de dérivation BIP32 configurable
derivation_path = m/44'/0'/0'
# Profondeur de scan configurable  
scan_depth = 20
"""
        
        try:
            with open(self.config_file, 'w') as f:
                f.write(default_config)
            print(f"✅ Fichier {self.config_file} créé avec succès!")
            print("📝 Veuillez maintenant éditer ce fichier avec votre mnémonique de 12 mots")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la création du fichier: {e}")
            return False
    
    def update_destination_address(self, new_address):
        """Met à jour l'adresse de destination dans config.ini."""
        if not self.config:
            return False, "Configuration non chargée"
        
        try:
            # S'assurer que la section Transaction existe
            if not self.config.has_section('Transaction'):
                self.config.add_section('Transaction')
            
            # Mettre à jour l'adresse
            self.config.set('Transaction', 'destination_address', new_address)
            
            # Sauvegarder dans le fichier
            with open(self.config_file, 'w') as f:
                self.config.write(f)
            
            return True, "Adresse de destination mise à jour avec succès"
            
        except Exception as e:
            return False, f"Erreur lors de la mise à jour: {e}"
    
    def update_transaction_amount(self, new_amount):
        """Met à jour le montant de transaction dans config.ini."""
        if not self.config:
            return False, "Configuration non chargée"
        
        try:
            # S'assurer que la section Transaction existe
            if not self.config.has_section('Transaction'):
                self.config.add_section('Transaction')
            
            # Mettre à jour le montant
            self.config.set('Transaction', 'amount_to_send_bsv', str(new_amount))
            
            # Sauvegarder dans le fichier
            with open(self.config_file, 'w') as f:
                self.config.write(f)
            
            return True, "Montant de transaction mis à jour avec succès"
            
        except Exception as e:
            return False, f"Erreur lors de la mise à jour: {e}"
    
    def update_fee_per_byte(self, new_fee):
        """Met à jour les frais par byte dans config.ini."""
        if not self.config:
            return False, "Configuration non chargée"
        
        try:
            # S'assurer que la section Transaction existe
            if not self.config.has_section('Transaction'):
                self.config.add_section('Transaction')
            
            # Mettre à jour les frais
            self.config.set('Transaction', 'fee_per_byte', str(new_fee))
            
            # Sauvegarder dans le fichier
            with open(self.config_file, 'w') as f:
                self.config.write(f)
            
            return True, "Frais par byte mis à jour avec succès"
            
        except Exception as e:
            return False, f"Erreur lors de la mise à jour: {e}"

    def update_derivation_path(self, new_path):
        """Met à jour le chemin de dérivation dans config.ini."""
        if not self.config:
            return False, "Configuration non chargée"
        
        # Valider le format du chemin de dérivation
        if not self._validate_derivation_path(new_path):
            return False, "Format de chemin de dérivation invalide"
        
        try:
            # S'assurer que la section Wallet existe
            if not self.config.has_section('Wallet'):
                self.config.add_section('Wallet')
            
            # Mettre à jour le chemin
            self.config.set('Wallet', 'derivation_path', new_path)
            
            # Sauvegarder dans le fichier
            with open(self.config_file, 'w') as f:
                self.config.write(f)
            
            return True, "Chemin de dérivation mis à jour avec succès"
            
        except Exception as e:
            return False, f"Erreur lors de la mise à jour: {e}"
    
    def update_scan_depth(self, new_depth):
        """Met à jour la profondeur de scan dans config.ini."""
        if not self.config:
            return False, "Configuration non chargée"
        
        try:
            depth = int(new_depth)
            if depth < 1 or depth > 1000:
                return False, "Profondeur de scan doit être entre 1 et 1000"
        except ValueError:
            return False, "Profondeur de scan doit être un nombre entier"
        
        try:
            # S'assurer que la section Wallet existe
            if not self.config.has_section('Wallet'):
                self.config.add_section('Wallet')
            
            # Mettre à jour la profondeur
            self.config.set('Wallet', 'scan_depth', str(depth))
            
            # Sauvegarder dans le fichier
            with open(self.config_file, 'w') as f:
                self.config.write(f)
            
            return True, "Profondeur de scan mise à jour avec succès"
            
        except Exception as e:
            return False, f"Erreur lors de la mise à jour: {e}"
    
    def _validate_derivation_path(self, path):
        """Valide le format d'un chemin de dérivation BIP32."""
        import re
        
        # Format BIP32: m/purpose'/coin_type'/account'/change/index
        # On accepte jusqu'à m/x'/x'/x' (3 niveaux avec hardened)
        pattern = r"^m(/\d+'?){1,5}$"
        
        if not re.match(pattern, path):
            return False
        
        # Vérifier les valeurs communes
        parts = path.split('/')
        if len(parts) < 2:
            return False
        
        # m/ doit être présent
        if parts[0] != 'm':
            return False
        
        return True