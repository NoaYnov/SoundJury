#!/usr/bin/env python3
"""
Test intégral du système SoundJury avec authentification
"""

def test_complete_system():
    print("🧪 Test complet du système SoundJury...")
    
    # Test 1: Système d'authentification
    print("\n1. Test du système d'authentification...")
    try:
        from auth import user_manager
        from ratings import get_track_id, add_rating, get_rating
        print("   ✅ Modules d'authentification importés")
    except ImportError as e:
        print(f"   ❌ Erreur d'import: {e}")
        return False
    
    # Test 2: Création d'utilisateur test
    print("\n2. Test de création d'utilisateur...")
    test_email = "testuser@example.com"
    user, error = user_manager.create_user(test_email, "password123", "TestUser")
    
    if error and "existe déjà" in error:
        print("   ✅ Utilisateur existe déjà")
        user = user_manager.get_user(test_email)
    elif user:
        print("   ✅ Utilisateur créé avec succès")
        user_manager.verify_user(test_email)  # Vérifier automatiquement
    else:
        print(f"   ❌ Erreur: {error}")
        return False
    
    # Test 3: Système de notation avec utilisateur
    print("\n3. Test du système de notation authentifié...")
    
    # Test avec utilisateur connecté
    success, error_msg = add_rating("Test Artist", "Test Song", 5, test_email)
    if success:
        print("   ✅ Note ajoutée avec succès")
    else:
        if "déjà noté" in error_msg:
            print("   ✅ Protection contre double vote fonctionnelle")
        else:
            print(f"   ❌ Erreur: {error_msg}")
    
    # Test sans utilisateur
    success, error_msg = add_rating("Test Artist 2", "Test Song 2", 4, None)
    if not success and "non connecté" in error_msg:
        print("   ✅ Protection utilisateur non connecté fonctionnelle")
    else:
        print("   ❌ La protection n'a pas fonctionné")
    
    # Test 4: Vérification des données
    print("\n4. Vérification des données...")
    rating_info = get_rating("Test Artist", "Test Song")
    if rating_info.get("count", 0) > 0:
        print(f"   ✅ Données sauvegardées: {rating_info['average']}/5 ({rating_info['count']} votes)")
    else:
        print("   ❌ Aucune donnée trouvée")
    
    # Test 5: Fichiers créés
    print("\n5. Vérification des fichiers...")
    import os
    files_to_check = ["users.json", "ratings.json"]
    for file in files_to_check:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"   ✅ {file} créé ({size} bytes)")
        else:
            print(f"   ⚠️ {file} non trouvé")
    
    # Test 6: Flask et templates
    print("\n6. Vérification des templates...")
    template_files = [
        "templates/base.html",
        "templates/login.html", 
        "templates/register.html",
        "templates/index.html",
        "templates/home.html"
    ]
    
    for template in template_files:
        if os.path.exists(template):
            print(f"   ✅ {template} présent")
        else:
            print(f"   ❌ {template} manquant")
    
    print("\n🎉 Test complet terminé !")
    print("\n🚀 Pour démarrer l'application :")
    print("   python app.py")
    print("   Puis ouvrez http://localhost:5000")
    
    return True

if __name__ == "__main__":
    test_complete_system()
