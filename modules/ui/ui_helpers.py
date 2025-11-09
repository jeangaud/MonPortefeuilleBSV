"""
ui_helpers.py
=============
Utilitaires partagés pour l'interface utilisateur BSV Wallet v4.0

Responsabilités:
- Formatage des montants BSV/satoshis
- Validation des entrées utilisateur
- Fonctions d'affichage communes
- Utilitaires de conversion
- Helpers pour l'interface

Ce module contient toutes les fonctions utilitaires partagées
entre les différents modules UI pour éviter la duplication de code.
"""

from decimal import Decimal
import re

class UIHelpers:
    """Classe utilitaire pour les fonctions communes de l'interface utilisateur."""
    
    # Constantes
    SATOSHIS_PER_BSV = 100000000
    DUST_LIMIT = 546  # satoshis
    
    @staticmethod
    def format_bsv_amount(satoshis, show_satoshis=True):
        """
        Formate un montant en satoshis vers un affichage BSV lisible.
        
        Args:
            satoshis (int): Montant en satoshis
            show_satoshis (bool): Afficher aussi les satoshis
            
        Returns:
            str: Montant formaté (ex: "0.00100000 BSV (100000 satoshis)")
        """
        bsv_amount = Decimal(satoshis) / UIHelpers.SATOSHIS_PER_BSV
        formatted = f"{bsv_amount:.8f} BSV"
        
        if show_satoshis and satoshis != 0:
            formatted += f" ({satoshis} satoshis)"
            
        return formatted
    
    @staticmethod
    def format_fee_estimate(fee_satoshis, tx_size_bytes):
        """
        Formate une estimation de frais avec détails.
        
        Args:
            fee_satoshis (int): Frais en satoshis
            tx_size_bytes (int): Taille de transaction en bytes
            
        Returns:
            str: Frais formatés avec détails
        """
        fee_per_byte = fee_satoshis / tx_size_bytes if tx_size_bytes > 0 else 0
        bsv_amount = UIHelpers.format_bsv_amount(fee_satoshis, False)
        
        return f"{bsv_amount} ({fee_per_byte:.1f} sat/byte, {tx_size_bytes} bytes)"
    
    @staticmethod
    def validate_bsv_amount(amount_str):
        """
        Valide et convertit une chaîne de montant BSV.
        
        Args:
            amount_str (str): Montant en chaîne
            
        Returns:
            tuple: (success: bool, value: float, error: str)
        """
        if not amount_str or not amount_str.strip():
            return False, 0.0, "Montant vide"
        
        try:
            amount = float(amount_str.strip())
            
            if amount <= 0:
                return False, 0.0, "Le montant doit être positif"
            
            if amount < (UIHelpers.DUST_LIMIT / UIHelpers.SATOSHIS_PER_BSV):
                return False, 0.0, f"Montant trop petit (dust limit: {UIHelpers.DUST_LIMIT} satoshis)"
            
            if amount > 21000000:  # Plus que le total de Bitcoin
                return False, 0.0, "Montant trop élevé"
                
            return True, amount, ""
            
        except ValueError:
            return False, 0.0, "Format de montant invalide (ex: 0.001)"
    
    @staticmethod
    def validate_fee_per_byte(fee_str):
        """
        Valide et convertit des frais par byte.
        
        Args:
            fee_str (str): Frais en chaîne
            
        Returns:
            tuple: (success: bool, value: int, error: str)
        """
        if not fee_str or not fee_str.strip():
            return False, 0, "Frais vides"
        
        try:
            fee = int(fee_str.strip())
            
            if fee <= 0:
                return False, 0, "Les frais doivent être positifs"
            
            if fee > 10000:
                return False, 0, "Frais excessivement élevés (>10000 sat/byte)"
                
            return True, fee, ""
            
        except ValueError:
            return False, 0, "Format de frais invalide (nombre entier attendu)"
    
    @staticmethod
    def validate_derivation_path(path_str):
        """
        Valide un chemin de dérivation BIP32.
        
        Args:
            path_str (str): Chemin de dérivation
            
        Returns:
            tuple: (success: bool, error: str)
        """
        if not path_str or not path_str.strip():
            return False, "Chemin vide"
        
        path = path_str.strip()
        
        # Vérifier le format de base
        if not path.startswith('m/'):
            return False, "Le chemin doit commencer par 'm/'"
        
        # Pattern pour valider le format BIP32
        pattern = r"^m(/\d+'?){1,5}$"
        
        if not re.match(pattern, path):
            return False, "Format invalide (ex: m/44'/0'/0')"
        
        # Vérifier la longueur raisonnable
        parts = path.split('/')
        if len(parts) < 2 or len(parts) > 6:
            return False, "Chemin trop court ou trop long"
            
        return True, ""
    
    @staticmethod
    def validate_scan_depth(depth_str):
        """
        Valide une profondeur de scan.
        
        Args:
            depth_str (str): Profondeur en chaîne
            
        Returns:
            tuple: (success: bool, value: int, error: str)
        """
        if not depth_str or not depth_str.strip():
            return False, 0, "Profondeur vide"
        
        try:
            depth = int(depth_str.strip())
            
            if depth < 1:
                return False, 0, "La profondeur doit être d'au moins 1"
            
            if depth > 1000:
                return False, 0, "Profondeur maximale: 1000 adresses"
                
            return True, depth, ""
            
        except ValueError:
            return False, 0, "Format invalide (nombre entier attendu)"
    
    @staticmethod
    def format_address_display(address, addr_type="Bitcoin", truncate=True):
        """
        Formate l'affichage d'une adresse avec son type.
        
        Args:
            address (str): Adresse à afficher
            addr_type (str): Type d'adresse ("Bitcoin", "Paymail", etc.)
            truncate (bool): Tronquer les adresses longues
            
        Returns:
            str: Adresse formatée
        """
        if not address:
            return "❌ Adresse vide"
        
        # Icône selon le type
        icons = {
            "Bitcoin": "🔗",
            "Paymail": "📧",
            "Unknown": "❓"
        }
        icon = icons.get(addr_type, "❓")
        
        # Tronquer si nécessaire
        if truncate and len(address) > 40 and addr_type == "Bitcoin":
            displayed_addr = f"{address[:16]}...{address[-8:]}"
        else:
            displayed_addr = address
        
        return f"{icon} {displayed_addr} ({addr_type})"
    
    @staticmethod
    def format_transaction_summary(tx_data):
        """
        Formate un résumé de transaction pour affichage.
        
        Args:
            tx_data (dict): Données de transaction
            
        Returns:
            str: Résumé formaté
        """
        lines = []
        lines.append("💰 RÉSUMÉ DE LA TRANSACTION:")
        
        # Destination
        if tx_data.get('is_paymail', False):
            lines.append(f"   📧 Paymail: {tx_data['paymail_address']}")
            lines.append(f"   🔗 Adresse résolue: {tx_data['destination']}")
            if tx_data.get('paymail_memo'):
                lines.append(f"   💬 Memo: {tx_data['paymail_memo']}")
        else:
            addr_display = UIHelpers.format_address_display(tx_data['destination'], "Bitcoin", True)
            lines.append(f"   Destination: {addr_display}")
        
        # Montants
        lines.append(f"   💰 Montant: {UIHelpers.format_bsv_amount(int(tx_data['amount'] * UIHelpers.SATOSHIS_PER_BSV))}")
        lines.append(f"   ⚡ Frais: {UIHelpers.format_bsv_amount(int(tx_data['fee'] * UIHelpers.SATOSHIS_PER_BSV))}")
        lines.append(f"   🔄 Change: {UIHelpers.format_bsv_amount(int(tx_data['change'] * UIHelpers.SATOSHIS_PER_BSV))}")
        
        # Détails techniques
        lines.append(f"   📦 UTXOs: {tx_data['utxo_count']} (de {tx_data['address_count']} adresses)")
        
        return "\n".join(lines)
    
    @staticmethod
    def show_progress_indicator(current, total, description="Progression"):
        """
        Affiche un indicateur de progression simple.
        
        Args:
            current (int): Étape actuelle
            total (int): Total d'étapes
            description (str): Description de la progression
        """
        if total <= 0:
            return
        
        percentage = (current / total) * 100
        bar_length = 30
        filled_length = int(bar_length * current // total)
        
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        print(f"\r{description}: |{bar}| {percentage:.1f}% ({current}/{total})", end='', flush=True)
        
        if current >= total:
            print()  # Nouvelle ligne à la fin
    
    @staticmethod
    def confirm_action(message, require_yes=False):
        """
        Demande confirmation pour une action.
        
        Args:
            message (str): Message de confirmation
            require_yes (bool): Exiger "oui" au lieu de "o"
            
        Returns:
            bool: True si confirmé
        """
        if require_yes:
            response = input(f"{message} (oui/non): ").lower().strip()
            return response == 'oui'
        else:
            response = input(f"{message} (o/n): ").lower().strip()
            return response in ['o', 'oui', 'y', 'yes']
    
    @staticmethod
    def format_balance_summary(addresses_with_funds, total_balance):
        """
        Formate un résumé de balance pour affichage.
        
        Args:
            addresses_with_funds (list): Liste des adresses avec fonds
            total_balance (int): Balance totale en satoshis
            
        Returns:
            str: Résumé formaté
        """
        if not addresses_with_funds:
            return "💰 Aucun solde trouvé sur les adresses scannées."
        
        lines = []
        lines.append(f"🎉 TOTAL DISPONIBLE: {UIHelpers.format_bsv_amount(total_balance)}")
        lines.append(f"   Réparti sur {len(addresses_with_funds)} adresses")
        
        if len(addresses_with_funds) <= 5:
            lines.append("\nDétail des adresses:")
            for addr_info in addresses_with_funds:
                balance_display = UIHelpers.format_bsv_amount(addr_info['balance'], False)
                lines.append(f"   • Adresse {addr_info['index']}: {balance_display}")
        else:
            lines.append(f"\n💡 Utilisez l'option 'Balance détaillée' pour voir toutes les adresses")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_config_status(config_data):
        """
        Formate le statut de configuration pour affichage.
        
        Args:
            config_data (dict): Données de configuration
            
        Returns:
            str: Statut formaté
        """
        lines = []
        
        # Mnémonique
        mnemonic_info = config_data.get('mnemonic', {})
        if mnemonic_info.get('configured'):
            word_count = mnemonic_info.get('word_count', 0)
            valid = mnemonic_info.get('valid', False)
            status = "✅ Valide" if valid else "⚠️ Invalide"
            lines.append(f"Mnémonique: {status} ({word_count} mots)")
        else:
            lines.append("Mnémonique: ❌ Non configurée")
        
        # Transaction
        tx_info = config_data.get('transaction', {})
        if tx_info:
            dest_status = "✅" if tx_info.get('destination_configured') else "❌"
            lines.append(f"Destination: {dest_status} {tx_info.get('destination_address', 'N/A')}")
            lines.append(f"Montant: {tx_info.get('amount', 'N/A')} BSV")
            lines.append(f"Frais: {tx_info.get('fee_per_byte', 'N/A')} sat/byte")
        
        return "\n".join(lines)
    
    @staticmethod
    def get_user_choice(prompt, valid_choices, case_sensitive=False):
        """
        Demande un choix à l'utilisateur avec validation.
        
        Args:
            prompt (str): Message d'invite
            valid_choices (list): Choix valides
            case_sensitive (bool): Sensible à la casse
            
        Returns:
            str: Choix validé de l'utilisateur
        """
        while True:
            choice = input(f"{prompt}: ").strip()
            
            if not case_sensitive:
                choice = choice.lower()
                valid_choices = [c.lower() for c in valid_choices]
            
            if choice in valid_choices:
                return choice
            
            print(f"❌ Choix invalide. Options valides: {', '.join(valid_choices)}")
    
    @staticmethod
    def format_time_duration(seconds):
        """
        Formate une durée en secondes vers un format lisible.
        
        Args:
            seconds (int): Durée en secondes
            
        Returns:
            str: Durée formatée
        """
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds}s"
        else:
            hours = seconds // 3600
            remaining_minutes = (seconds % 3600) // 60
            return f"{hours}h {remaining_minutes}m"
    
    @staticmethod
    def truncate_text(text, max_length, suffix="..."):
        """
        Tronque un texte à une longueur maximale.
        
        Args:
            text (str): Texte à tronquer
            max_length (int): Longueur maximale
            suffix (str): Suffixe à ajouter si tronqué
            
        Returns:
            str: Texte tronqué ou original
        """
        if not text or len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def format_network_status(is_connected, server_info=None):
        """
        Formate le statut de connexion réseau.
        
        Args:
            is_connected (bool): État de connexion
            server_info (dict): Informations du serveur
            
        Returns:
            str: Statut formaté
        """
        if is_connected:
            status = "🟢 Connecté"
            if server_info:
                server = server_info.get('server', 'Inconnu')
                status += f" à {server}"
        else:
            status = "🔴 Déconnecté"
        
        return status
    
    @staticmethod
    def safe_input(prompt, input_type="str", default=None):
        """
        Entrée utilisateur sécurisée avec gestion d'erreurs.
        
        Args:
            prompt (str): Message d'invite
            input_type (str): Type attendu ("str", "int", "float")
            default: Valeur par défaut
            
        Returns:
            Valeur saisie convertie ou None si erreur
        """
        try:
            user_input = input(f"{prompt}: ").strip()
            
            if not user_input and default is not None:
                return default
            
            if input_type == "int":
                return int(user_input)
            elif input_type == "float":
                return float(user_input)
            else:
                return user_input
                
        except (ValueError, KeyboardInterrupt):
            return None