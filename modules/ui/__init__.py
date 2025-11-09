"""
modules/ui/__init__.py - Phase 3
=================================
Package d'interface utilisateur modulaire pour BSV Wallet v4.0

Ce package contient tous les modules d'interface utilisateur segmentés
pour améliorer la lisibilité et la maintenabilité du code.

Modules disponibles (Phase 3):
- balance_ui: Interface de gestion des balances ✅ (NOUVEAU)
- send_ui: Interface d'envoi de fonds ✅ (NOUVEAU)
- receive_ui: Interface de réception ✅ (NOUVEAU)
- verification_ui: Interface de vérification ✅ (NOUVEAU)
- paymail_ui: Interface Paymail complète ✅
- config_ui: Interface Configuration complète ✅
- ui_helpers: Utilitaires partagés ✅
"""

# Import de tous les modules UI disponibles
from .ui_helpers import UIHelpers
from .config_ui import ConfigUI
from .paymail_ui import PaymailUI
from .balance_ui import BalanceUI
from .send_ui import SendUI
from .receive_ui import ReceiveUI
from .verification_ui import VerificationUI


# Liste des modules exportés pour être accessibles depuis l'extérieur
__all__ = [
    'UIHelpers',
    'ConfigUI',
    'PaymailUI',
    'BalanceUI',
    'SendUI',
    'ReceiveUI',
    'VerificationUI',
]

# Version du package UI
__version__ = "3.0.0"  # Mis à jour pour la Phase 3

# Métadonnées du package
__author__ = "BSV Wallet Team"
__description__ = "Interface utilisateur modulaire pour BSV Wallet v4.0 - Phase 3"

# Informations sur la segmentation
SEGMENTATION_STATUS = {
    "phase": 3,
    "status": "Segmentation complète",
    "completed_modules": [
        "UIHelpers", "ConfigUI", "PaymailUI", 
        "BalanceUI", "SendUI", "ReceiveUI", "VerificationUI"
    ],
    "architecture": "Modulaire et entièrement segmenté"
}
