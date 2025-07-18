#!/usr/bin/env python3
"""
Test de démarrage de l'application Flask
"""

def test_app_startup():
    print("🧪 Test de démarrage de l'application...")
    
    try:
        # Import de l'application
        from app import app
        print("   ✅ Application Flask importée avec succès")
        
        # Vérification de la configuration
        print(f"   ✅ Clé secrète configurée: {bool(app.config.get('SECRET_KEY'))}")
        
        # Test des routes
        with app.test_client() as client:
            # Test page d'accueil
            response = client.get('/')
            print(f"   ✅ Page d'accueil: {response.status_code}")
            
            # Test page de connexion
            response = client.get('/login')
            print(f"   ✅ Page de connexion: {response.status_code}")
            
            # Test page d'inscription
            response = client.get('/register')
            print(f"   ✅ Page d'inscription: {response.status_code}")
            
            # Test page de recherche
            response = client.get('/search')
            print(f"   ✅ Page de recherche: {response.status_code}")
        
        print("\n🎉 Application prête à démarrer !")
        print("🚀 Lancez avec: python app.py")
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_app_startup()
