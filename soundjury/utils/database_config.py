# Configuration pour les options de base de données
import os
try:
    from dotenv import load_dotenv
    # Charger les variables d'environnement depuis le fichier .env du dossier parent
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    load_dotenv(dotenv_path)
except ImportError:
    pass  # python-dotenv n'est pas installé, on continue sans

# Option 1: Stockage JSON local (développement)
USE_JSON_STORAGE = False  # Changé à False pour utiliser Supabase

# Option 2: MongoDB Atlas (gratuit jusqu'à 512MB)
MONGODB_URI = os.getenv('MONGODB_URI', '')

# Option 3: Supabase (gratuit jusqu'à 500MB)
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')

# Option 4: PlanetScale (MySQL gratuit)
PLANETSCALE_DATABASE_URL = os.getenv('PLANETSCALE_DATABASE_URL', '')

# Option 5: Firebase Firestore
FIREBASE_CREDENTIALS = os.getenv('FIREBASE_CREDENTIALS', '')

# Choix de la base de données (par ordre de priorité)
def get_database_config():
    if SUPABASE_URL and SUPABASE_KEY and not USE_JSON_STORAGE:
        return 'supabase'
    elif MONGODB_URI and not USE_JSON_STORAGE:
        return 'mongodb'
    elif PLANETSCALE_DATABASE_URL and not USE_JSON_STORAGE:
        return 'planetscale'
    elif FIREBASE_CREDENTIALS and not USE_JSON_STORAGE:
        return 'firebase'
    else:
        return 'json'
