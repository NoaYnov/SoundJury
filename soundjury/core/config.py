"""
Configuration de l'application SoundJury
"""
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)

class Config:
    """Configuration de base"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configuration Supabase
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    # Configuration Flask-Login
    REMEMBER_COOKIE_DURATION = 86400  # 1 jour
    
    # Configuration de session
    PERMANENT_SESSION_LIFETIME = 86400  # 1 jour
    
    # Configuration API Deezer
    DEEZER_API_BASE = "https://api.deezer.com"

class DevelopmentConfig(Config):
    """Configuration de développement"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuration de production"""
    DEBUG = False
    TESTING = False

# Configuration par défaut
config = DevelopmentConfig()
