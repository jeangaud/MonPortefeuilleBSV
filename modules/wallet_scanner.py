"""
wallet_scanner.py
=================
Module de scan d'adresses pour BSV Wallet v4.0

Responsabilités:
- Scanner les adresses HD pour trouver les fonds
- Récupérer les UTXOs et balances
- Optimiser les requêtes réseau
- Formater les résultats de scan
"""

from decimal import Decimal

class WalletScanner:
    """Scanner d'adresses pour le portefeuille BSV."""
    
    def __init__(self, crypto_manager, network_manager, scan_depth=20):
        self.crypto = crypto_manager
        self.network = network_manager
        self.scan_depth = scan_depth
        self.satoshis_per_bsv = 100000000
    
    def scan_all_addresses(self):
        """Scanne toutes les adresses et retourne celles avec des fonds."""
        print("-" * 60)
        print("SCAN COMPLET DE TOUTES LES ADRESSES AVEC FONDS")
        print("-" * 60)
        
        addresses_with_funds = []
        total_balance = 0
        
        for i in range(self.scan_depth):
            addr_info = self.crypto.get_address_info(i)
            if not addr_info:
                continue
            
            address = addr_info['address']
            scripthash = self.crypto.address_to_scripthash(address)
            if not scripthash:
                continue

            balance = self.network.get_balance(scripthash)
            if balance is None:
                break

            confirmed = balance.get('confirmed', 0)
            unconfirmed = balance.get('unconfirmed', 0)
            total_addr_balance = confirmed + unconfirmed
            
            if total_addr_balance > 0:
                # Récupérer les UTXOs
                utxos = self.network.get_utxos(scripthash)
                if utxos:
                    addr_info.update({
                        'balance': total_addr_balance,
                        'confirmed': confirmed,
                        'unconfirmed': unconfirmed,
                        'utxos': utxos
                    })
                    addresses_with_funds.append(addr_info)
                    total_balance += total_addr_balance
                    
                    print(f"✅ Adresse {i}: {address}")
                    print(f"   Solde: {Decimal(total_addr_balance) / self.satoshis_per_bsv:.8f} BSV")
                    if unconfirmed > 0:
                        print(f"   Confirmé: {Decimal(confirmed) / self.satoshis_per_bsv:.8f} BSV")
                        print(f"   Non confirmé: {Decimal(unconfirmed) / self.satoshis_per_bsv:.8f} BSV")
                    print(f"   UTXOs: {len(utxos)}")
                    print()
        
        print("-" * 60)
        print(f"RÉSUMÉ: {len(addresses_with_funds)} adresses avec fonds")
        print(f"TOTAL: {Decimal(total_balance) / self.satoshis_per_bsv:.8f} BSV")
        print("-" * 60)
        
        return addresses_with_funds, total_balance
    
    def get_single_address_info(self, index):
        """Récupère les informations détaillées d'une seule adresse."""
        addr_info = self.crypto.get_address_info(index)
        if not addr_info:
            return None
        
        address = addr_info['address']
        scripthash = self.crypto.address_to_scripthash(address)
        if not scripthash:
            return None
        
        balance = self.network.get_balance(scripthash)
        if balance is None:
            return None
        
        confirmed = balance.get('confirmed', 0)
        unconfirmed = balance.get('unconfirmed', 0)
        total_balance = confirmed + unconfirmed
        
        utxos = self.network.get_utxos(scripthash) if total_balance > 0 else []
        history = self.network.get_history(scripthash)
        
        addr_info.update({
            'balance': total_balance,
            'confirmed': confirmed,
            'unconfirmed': unconfirmed,
            'utxos': utxos or [],
            'history': history or [],
            'scripthash': scripthash
        })
        
        return addr_info
    
    def format_balance_display(self, addresses_with_funds, total_balance):
        """Formate l'affichage des balances pour l'interface."""
        if not addresses_with_funds:
            return f"Aucun solde trouvé sur les {self.scan_depth} premières adresses."
        
        result = []
        result.append(f"🎉 TOTAL DISPONIBLE: {Decimal(total_balance) / self.satoshis_per_bsv:.8f} BSV")
        result.append(f"   Réparti sur {len(addresses_with_funds)} adresses")
        
        if len(addresses_with_funds) <= 5:
            result.append("\nDétail des adresses:")
            for addr_info in addresses_with_funds:
                balance_bsv = Decimal(addr_info['balance']) / self.satoshis_per_bsv
                result.append(f"   • Adresse {addr_info['index']}: {balance_bsv:.8f} BSV")
        
        return "\n".join(result)
    
    def check_address_has_funds(self, address):
        """Vérifie rapidement si une adresse a des fonds."""
        scripthash = self.crypto.address_to_scripthash(address)
        if not scripthash:
            return False, 0
        
        balance = self.network.get_balance(scripthash)
        if not balance:
            return False, 0
        
        total_balance = balance.get('confirmed', 0) + balance.get('unconfirmed', 0)
        return total_balance > 0, total_balance
