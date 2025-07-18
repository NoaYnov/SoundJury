#!/usr/bin/env python3
"""
Script de test pour le système d'authentification
"""

import sys
import os

# Ajouter le dossier parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth import user_manager, EmailVerification
from werkzeug.security import generate_password_hash

def test_auth_system():
    print("🧪 Test du système d'authentification...")
    
    # Test 1: Créer un utilisateur
    print("\n1. Création d'utilisateur de test...")
    test_email = "test@soundjury.com"
    test_password = "motdepasse123"
    
    user, error = user_manager.create_user(test_email, test_password, "TestUser")
    
    if error:
        if "existe déjà" in error:
            print(f"   ✅ Utilisateur {test_email} existe déjà")
            user = user_manager.get_user(test_email)
        else:
            print(f"   ❌ Erreur: {error}")
            return
    else:
        print(f"   ✅ Utilisateur créé: {test_email}")
    
    # Test 2: Vérifier le mot de passe
    print("\n2. Vérification du mot de passe...")
    if user and user.check_password(test_password):
        print("   ✅ Mot de passe correct")
    else:
        print("   ❌ Mot de passe incorrect")
        return
    
    # Test 3: Vérifier l'utilisateur
    print("\n3. Vérification du compte...")
    if user_manager.verify_user(test_email):
        print("   ✅ Compte vérifié avec succès")
    else:
        print("   ❌ Erreur lors de la vérification")
    
    # Test 4: Vérifier le token
    print("\n4. Test du système de tokens...")
    verifier = EmailVerification("test-secret-key")
    token = verifier.generate_token(test_email)
    print(f"   📧 Token généré: {token[:20]}...")
    
    decoded_email = verifier.verify_token(token)
    if decoded_email == test_email:
        print("   ✅ Token valide")
    else:
        print("   ❌ Token invalide")
    
    # Test 5: Lister les utilisateurs
    print("\n5. Liste des utilisateurs:")
    users = user_manager.get_all_users()
    for u in users:
        status = "✅ Vérifié" if u.is_verified else "⚠️ Non vérifié"
        print(f"   👤 {u.email} ({u.username}) - {status}")
    
    print("\n✅ Tests d'authentification terminés !")

if __name__ == "__main__":
    test_auth_system()
