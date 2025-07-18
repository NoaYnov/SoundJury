# Système d'authentification pour SoundJury
import json
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask_login import UserMixin
from database_manager import get_database

# Fichier pour stocker les utilisateurs (mode JSON)
USERS_FILE = "users.json"

class User(UserMixin):
    def __init__(self, email, password_hash=None, is_verified=False, user_id=None, username=None):
        self.email = email
        self.password_hash = password_hash
        self.is_verified = is_verified
        self.id = user_id or email  # Flask-Login nécessite un id
        self.username = username or email.split('@')[0]
        self.created_at = datetime.now().isoformat()
    
    def set_password(self, password):
        """Hash et stocke le mot de passe"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Vérifie le mot de passe"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convertit l'utilisateur en dictionnaire pour stockage"""
        return {
            'email': self.email,
            'password_hash': self.password_hash,
            'is_verified': self.is_verified,
            'username': self.username,
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dict(data, email):
        """Crée un utilisateur depuis un dictionnaire"""
        user = User(email)
        user.password_hash = data.get('password_hash')
        user.is_verified = data.get('is_verified', False)
        user.username = data.get('username', email.split('@')[0])
        user.created_at = data.get('created_at', datetime.now().isoformat())
        return user

class UserManager:
    def __init__(self):
        self.db = get_database()
    
    def _load_users(self):
        """Charge les utilisateurs depuis le stockage"""
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_users(self, users_data):
        """Sauvegarde les utilisateurs"""
        try:
            with open(USERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, ensure_ascii=False, indent=2)
            return True
        except IOError:
            return False
    
    def create_user(self, email, password, username=None):
        """Crée un nouveau utilisateur"""
        users_data = self._load_users()
        
        if email in users_data:
            return None, "Un compte existe déjà avec cette adresse email"
        
        user = User(email, username=username)
        user.set_password(password)
        
        users_data[email] = user.to_dict()
        
        if self._save_users(users_data):
            return user, None
        else:
            return None, "Erreur lors de la création du compte"
    
    def get_user(self, email):
        """Récupère un utilisateur par email"""
        users_data = self._load_users()
        
        if email in users_data:
            return User.from_dict(users_data[email], email)
        return None
    
    def verify_user(self, email):
        """Marque un utilisateur comme vérifié"""
        users_data = self._load_users()
        
        if email in users_data:
            users_data[email]['is_verified'] = True
            return self._save_users(users_data)
        return False
    
    def get_all_users(self):
        """Récupère tous les utilisateurs (admin)"""
        users_data = self._load_users()
        return [User.from_dict(data, email) for email, data in users_data.items()]

class EmailVerification:
    def __init__(self, secret_key):
        self.serializer = URLSafeTimedSerializer(secret_key)
    
    def generate_token(self, email):
        """Génère un token de vérification pour un email"""
        return self.serializer.dumps(email, salt='email-verification')
    
    def verify_token(self, token, max_age=3600):
        """Vérifie un token de vérification (expire après 1h par défaut)"""
        try:
            email = self.serializer.loads(token, salt='email-verification', max_age=max_age)
            return email
        except:
            return None

# Instances globales
user_manager = UserManager()
email_verifier = None  # Sera initialisé dans app.py avec la clé secrète
