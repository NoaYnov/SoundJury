"""
Configuration globale de l'application SoundJury
"""
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Config:
    """Configuration principale de l'application"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # APIs Musicales
    DEEZER_API_URL = "https://api.deezer.com"
    
    # Email
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    
    # Chemins de fichiers
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    USERS_FILE = os.path.join(DATA_DIR, 'users.json')
    RATINGS_FILE = os.path.join(DATA_DIR, 'ratings.json')
    
    # Paramètres de l'application
    MAX_TRACKS_PER_REQUEST = 50
    DEFAULT_TRENDING_LIMIT = 10
    SESSION_LIFETIME_HOURS = 24
    
    @classmethod
    def init_app(cls, app):
        """Initialise la configuration Flask"""
        app.config.from_object(cls)
        
        # Créer les dossiers nécessaires
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        
        return app

# Configuration pour les différents environnements
class DevelopmentConfig(Config):
    """Configuration de développement"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Configuration de production"""
    DEBUG = False
    
class TestingConfig(Config):
    """Configuration de test"""
    TESTING = True
    DEBUG = True

# Mapping des configurations
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
