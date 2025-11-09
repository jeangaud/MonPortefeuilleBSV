"""
wallet_crypto.py - Version corrigée
==================================
Module cryptographique pour BSV Wallet v4.0

Responsabilités:
- Génération d'adresses à partir de clés BIP32
- Gestion des clés privées/publiques
- Conversion d'adresses en scripthash
- Utilitaires cryptographiques Bitcoin
"""

import hashlib
import base58
from bip_utils.bip.bip39 import Bip39SeedGenerator
from bip_utils.bip.bip32 import Bip32Secp256k1
from bip_utils.utils.crypto import Ripemd160

class WalletCrypto:
    """Gestionnaire cryptographique pour le portefeuille BSV."""
    
    def __init__(self):
        self.bip32_master = None
        self.derivation_path = "m/44'/0'/0'"  # Valeur par défaut corrigée
    
    def set_derivation_path(self, path):
        """Configure le chemin de dérivation BIP32."""
        # Nettoyer le chemin (enlever les espaces et caractères indésirables)
        cleaned_path = path.strip()
        
        # Valider le format de base
        if not cleaned_path.startswith('m/'):
            raise ValueError(f"Chemin de dérivation invalide: doit commencer par 'm/' - reçu: {cleaned_path}")
        
        # Corriger les apostrophes si nécessaire
        # Remplacer les apostrophes droites par des apostrophes simples
        cleaned_path = cleaned_path.replace("'", "'")
        
        # Validation basique du format
        parts = cleaned_path.split('/')
        if len(parts) < 2:
            raise ValueError(f"Chemin de dérivation trop court: {cleaned_path}")
        
        # Stocker le chemin validé
        self.derivation_path = cleaned_path
        print(f"📍 Chemin de dérivation configuré: {self.derivation_path}")
    
    def initialize_from_mnemonic(self, mnemonic, passcode=""):
        """Initialise le portefeuille à partir d'une mnémonique."""
        try:
            seed_bytes = Bip39SeedGenerator(mnemonic).Generate(passcode)
            self.bip32_master = Bip32Secp256k1.FromSeed(seed_bytes)
            return True, "Portefeuille initialisé avec succès"
        except ValueError as e:
            return False, f"Mnémonique BIP39 invalide: {str(e)}"
        except Exception as e:
            return False, f"Erreur lors de l'initialisation: {e}"
    
    def get_address_info(self, index):
        """Génère les informations d'adresse pour un index donné."""
        if not self.bip32_master:
            return None
        
        # Construire le chemin complet avec l'index
        specific_path = f"{self.derivation_path}/{index}"
        
        try:
            bip32_child = self.bip32_master.DerivePath(specific_path)
            address = self.generate_address_from_bip32(bip32_child)
            
            return {
                'index': index,
                'path': specific_path,
                'address': address,
                'bip32_node': bip32_child
            }
        except Exception as e:
            print(f"❌ Erreur génération adresse {index}: {e}")
            return None
    
    def generate_address_from_bip32(self, bip32_node):
        """Génère une adresse Bitcoin à partir d'un noeud BIP32."""
        pub_key_bytes = bip32_node.PublicKey().RawCompressed().ToBytes()
        sha256_hash = hashlib.sha256(pub_key_bytes).digest()
        ripemd160_hash = Ripemd160.QuickDigest(sha256_hash)
        payload = b'\x00' + ripemd160_hash
        checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
        address = base58.b58encode(payload + checksum).decode('utf-8')
        return address
    
    def address_to_scripthash(self, address):
        """Convertit une adresse BSV en scripthash pour le protocole ElectrumX."""
        try:
            decoded_address = base58.b58decode_check(address)
            payload = decoded_address[1:]
            script = b'\x76\xa9\x14' + payload + b'\x88\xac'
            sha256_hash = hashlib.sha256(script).digest()
            scripthash = sha256_hash[::-1].hex()
            return scripthash
        except Exception as e:
            print(f"   [Erreur] Impossible de convertir l'adresse '{address}'. Erreur: {e}")
            return None
    
    def get_pubkey_hash_from_address(self, address):
        """Extrait le hash de la clé publique d'une adresse Bitcoin."""
        try:
            decoded = base58.b58decode_check(address)
            return decoded[1:]  # Enlever le premier byte (version)
        except:
            return None
    
    def double_sha256(self, data):
        """Double SHA256 comme utilisé dans Bitcoin."""
        return hashlib.sha256(hashlib.sha256(data).digest()).digest()
    
    @staticmethod
    def validate_address(address):
        """Valide une adresse Bitcoin."""
        try:
            decoded = base58.b58decode_check(address)
            return len(decoded) == 21 and decoded[0] == 0  # Version byte pour mainnet
        except:
            return False