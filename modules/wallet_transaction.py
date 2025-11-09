"""
wallet_transaction.py
=====================
Module de gestion des transactions pour BSV Wallet v4.0

Responsabilités:
- Création de transactions multi-adresses
- Sélection optimale d'UTXOs
- Signature des transactions BSV (SIGHASH_FORKID)
- Gestion des frais et du change
"""

import struct
from decimal import Decimal
import ecdsa
from ecdsa import SigningKey, SECP256k1
from ecdsa.util import sigencode_der

class TransactionBuilder:
    """Constructeur de transactions pour BSV."""
    
    def __init__(self, crypto_manager):
        self.crypto = crypto_manager
        self.satoshis_per_bsv = 100000000
    
    def int_to_varint(self, n):
        """Convertit un entier en varint Bitcoin."""
        if n < 0xfd:
            return struct.pack('<B', n)
        elif n <= 0xffff:
            return struct.pack('<BH', 0xfd, n)
        elif n <= 0xffffffff:
            return struct.pack('<BI', 0xfe, n)
        else:
            return struct.pack('<BQ', 0xff, n)
    
    def is_canonical_signature(self, signature):
        """Vérifie si une signature est canonique (valeur S faible)."""
        if len(signature) < 8:
            return False
        
        try:
            if signature[0] != 0x30:
                return False
            
            r_length = signature[3]
            s_start = 4 + r_length + 2
            s_length = signature[s_start - 1]
            
            if s_start + s_length > len(signature):
                return False
            
            s_bytes = signature[s_start:s_start + s_length]
            s_int = int.from_bytes(s_bytes, 'big')
            
            n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
            return s_int <= n // 2
            
        except:
            return False
    
    def create_bch_sighash(self, tx_version, input_prevouts, input_sequences, outpoint, 
                          scriptcode, amount, sequence, output_hashes, locktime, sighash_type):
        """Crée le sighash pour Bitcoin Cash/BSV selon BIP143."""
        
        ss = struct.pack('<I', tx_version)
        ss += input_prevouts
        ss += input_sequences
        ss += outpoint
        ss += self.int_to_varint(len(scriptcode)) + scriptcode
        ss += struct.pack('<Q', amount)
        ss += sequence
        ss += output_hashes
        ss += struct.pack('<I', locktime)
        ss += struct.pack('<I', sighash_type)
        
        return self.crypto.double_sha256(ss)
    
    def select_utxos_for_amount(self, addresses_with_funds, target_amount, fee_per_byte):
        """Sélectionne les UTXOs optimaux pour le montant cible."""
        print(f"\n🎯 SÉLECTION D'UTXOs POUR {Decimal(target_amount) / self.satoshis_per_bsv:.8f} BSV")
        
        # Collecter tous les UTXOs disponibles avec leurs infos
        all_utxos = []
        for addr_info in addresses_with_funds:
            for utxo in addr_info['utxos']:
                all_utxos.append({
                    'utxo': utxo,
                    'address': addr_info['address'],
                    'bip32_node': addr_info['bip32_node'],
                    'index': addr_info['index']
                })
        
        # Trier par valeur décroissante pour optimiser
        all_utxos.sort(key=lambda x: x['utxo']['value'], reverse=True)
        
        selected_utxos = []
        selected_total = 0
        
        # Estimer les frais de base
        base_tx_size = 10 + (2 * 34)  # Version + outputs + locktime
        
        for utxo_info in all_utxos:
            utxo = utxo_info['utxo']
            
            # Ajouter cet UTXO
            selected_utxos.append(utxo_info)
            selected_total += utxo['value']
            
            # Calculer les frais avec ce nombre d'UTXOs
            estimated_size = base_tx_size + (len(selected_utxos) * 148)
            estimated_fee = estimated_size * fee_per_byte
            
            # Vérifier si on a assez
            if selected_total >= (target_amount + estimated_fee + 1000):  # +1000 marge
                print(f"✅ Sélection optimale trouvée:")
                print(f"   UTXOs sélectionnés: {len(selected_utxos)}")
                print(f"   Total input: {Decimal(selected_total) / self.satoshis_per_bsv:.8f} BSV")
                print(f"   Frais estimés: {Decimal(estimated_fee) / self.satoshis_per_bsv:.8f} BSV")
                print(f"   Change: {Decimal(selected_total - target_amount - estimated_fee) / self.satoshis_per_bsv:.8f} BSV")
                
                # Afficher les adresses utilisées
                used_addresses = {}
                for utxo_info in selected_utxos:
                    addr = utxo_info['address']
                    if addr not in used_addresses:
                        used_addresses[addr] = 0
                    used_addresses[addr] += utxo_info['utxo']['value']
                
                print(f"\n📍 ADRESSES UTILISÉES:")
                for addr, amount in used_addresses.items():
                    print(f"   {addr}: {Decimal(amount) / self.satoshis_per_bsv:.8f} BSV")
                
                return selected_utxos, selected_total, estimated_fee
        
        print("❌ Fonds insuffisants même en combinant toutes les adresses")
        return None, 0, 0
    
    def create_multi_address_transaction(self, selected_utxos, outputs, change_address):
        """Crée une transaction avec UTXOs de plusieurs adresses."""
        
        print(f"\n🔨 CRÉATION TRANSACTION MULTI-ADRESSES")
        print(f"   Inputs: {len(selected_utxos)} UTXOs")
        print(f"   Outputs: {len(outputs)} sorties")
        
        version = 1
        locktime = 0
        sighash_type = 0x41  # SIGHASH_ALL | SIGHASH_FORKID
        
        # Construire les sorties
        outputs_data = b''
        for output in outputs:
            value = struct.pack('<Q', output['value'])
            pubkey_hash = self.crypto.get_pubkey_hash_from_address(output['address'])
            if not pubkey_hash:
                print(f"ERREUR: Adresse de sortie invalide: {output['address']}")
                return None
            
            script = b'\x76\xa9\x14' + pubkey_hash + b'\x88\xac'
            script_length = self.int_to_varint(len(script))
            outputs_data += value + script_length + script
        
        # Calculer les hashes pour BIP143
        prevouts = b''
        sequences = b''
        for utxo_info in selected_utxos:
            utxo = utxo_info['utxo']
            prevouts += bytes.fromhex(utxo['tx_hash'])[::-1] + struct.pack('<I', utxo['tx_pos'])
            sequences += struct.pack('<I', 0xffffffff)
        
        hash_prevouts = self.crypto.double_sha256(prevouts)
        hash_sequence = self.crypto.double_sha256(sequences)
        hash_outputs = self.crypto.double_sha256(outputs_data)
        
        # Signer chaque input avec sa clé privée correspondante
        signed_inputs = b''
        
        for i, utxo_info in enumerate(selected_utxos):
            utxo = utxo_info['utxo']
            bip32_node = utxo_info['bip32_node']
            source_address = utxo_info['address']
            
            # Obtenir la clé privée pour cette adresse
            private_key_hex = bip32_node.PrivateKey().Raw().ToHex()
            private_key_bytes = bytes.fromhex(private_key_hex)
            signing_key = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
            public_key = signing_key.get_verifying_key().to_string('compressed')
            
            # Obtenir le pubkey hash de l'adresse source
            source_pubkey_hash = self.crypto.get_pubkey_hash_from_address(source_address)
            scriptcode = b'\x76\xa9\x14' + source_pubkey_hash + b'\x88\xac'
            
            # Préparer les données pour le sighash
            prev_hash = bytes.fromhex(utxo['tx_hash'])[::-1]
            prev_index = struct.pack('<I', utxo['tx_pos'])
            sequence = struct.pack('<I', 0xffffffff)
            outpoint = prev_hash + prev_index
            
            # Créer le sighash selon BIP143
            sighash = self.create_bch_sighash(
                version, hash_prevouts, hash_sequence, outpoint, 
                scriptcode, utxo['value'], sequence, hash_outputs, 
                locktime, sighash_type
            )
            
            print(f"   Signature input {i} (adresse {utxo_info['index']}): {sighash.hex()[:16]}...")
            
            # Signer
            signature = signing_key.sign_digest_deterministic(sighash, sigencode=sigencode_der)
            
            # Vérifier et corriger la canonicité
            if not self.is_canonical_signature(signature):
                r_length = signature[3]
                r = int.from_bytes(signature[4:4+r_length], 'big')
                s_start = 4 + r_length + 2
                s_length = signature[s_start-1]
                s = int.from_bytes(signature[s_start:s_start+s_length], 'big')
                
                n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
                
                if s > n // 2:
                    s = n - s
                
                r_bytes = r.to_bytes((r.bit_length() + 7) // 8, 'big')
                s_bytes = s.to_bytes((s.bit_length() + 7) // 8, 'big')
                
                if r_bytes[0] & 0x80:
                    r_bytes = b'\x00' + r_bytes
                if s_bytes[0] & 0x80:
                    s_bytes = b'\x00' + s_bytes
                
                signature = (b'\x30' + 
                            bytes([len(r_bytes) + len(s_bytes) + 4]) +
                            b'\x02' + bytes([len(r_bytes)]) + r_bytes +
                            b'\x02' + bytes([len(s_bytes)]) + s_bytes)
            
            signature += b'\x41'  # SIGHASH_ALL | SIGHASH_FORKID
            
            # Script de déverrouillage
            unlocking_script = (
                bytes([len(signature)]) + signature +
                bytes([len(public_key)]) + public_key
            )
            script_length = self.int_to_varint(len(unlocking_script))
            
            # Ajouter l'input signé
            signed_inputs += prev_hash + prev_index + script_length + unlocking_script + sequence
        
        # Transaction finale
        final_tx = (struct.pack('<I', version) + 
                    self.int_to_varint(len(selected_utxos)) + 
                    signed_inputs + 
                    self.int_to_varint(len(outputs)) + 
                    outputs_data + 
                    struct.pack('<I', locktime))
        
        print(f"✅ Transaction multi-adresses créée, taille: {len(final_tx)} bytes")
        return final_tx.hex()
