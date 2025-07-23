"""
Modèle User - Gestion des utilisateurs
"""
import json
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin):
    """Modèle utilisateur avec authentification"""
    
    def __init__(self, email: str, username: str, password_hash: str = None, 
                 is_verified: bool = False, verification_token: str = None, id: str = None):
        self.id = id or email  # Utiliser l'ID Supabase si fourni, sinon l'email
        self.email = email
        self.username = username
        self.password_hash = password_hash
        self.is_verified = is_verified
        self.verification_token = verification_token
        self.created_at = datetime.now().isoformat()
        self.last_login = None
        
    def get_id(self) -> str:
        """Retourne l'ID unique de l'utilisateur pour Flask-Login"""
        return self.id or self.email
    
    def set_password(self, password: str) -> None:
        """Définit le mot de passe hashé"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Vérifie le mot de passe"""
        return check_password_hash(self.password_hash, password)
    
    def generate_verification_token(self) -> str:
        """Génère un token de vérification"""
        data = f"{self.email}_{self.username}_{datetime.now().isoformat()}"
        self.verification_token = hashlib.md5(data.encode()).hexdigest()
        return self.verification_token
    
    def verify_account(self) -> None:
        """Vérifie le compte utilisateur"""
        self.is_verified = True
        self.verification_token = None
    
    def update_last_login(self) -> None:
        """Met à jour la date de dernière connexion"""
        self.last_login = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'utilisateur en dictionnaire"""
        return {
            'email': self.email,
            'username': self.username,
            'password_hash': self.password_hash,
            'is_verified': self.is_verified,
            'verification_token': self.verification_token,
            'created_at': self.created_at,
            'last_login': self.last_login
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Crée un utilisateur à partir d'un dictionnaire"""
        user = cls(
            email=data['email'],
            username=data['username'],
            password_hash=data.get('password_hash'),
            is_verified=data.get('is_verified', False),
            verification_token=data.get('verification_token')
        )
        user.created_at = data.get('created_at', user.created_at)
        user.last_login = data.get('last_login')
        return user
    
    def __repr__(self) -> str:
        return f"<User {self.username} ({self.email})>"

class UserManager:
    """Gestionnaire des utilisateurs avec persistance JSON"""
    
    def __init__(self, users_file: str):
        self.users_file = users_file
        self._users = self._load_users()
    
    def _load_users(self) -> Dict[str, User]:
        """Charge les utilisateurs depuis le fichier JSON"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    email: User.from_dict(user_data) 
                    for email, user_data in data.items()
                }
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            print(f"Erreur lors du chargement de {self.users_file}")
            return {}
    
    def _save_users(self) -> bool:
        """Sauvegarde les utilisateurs dans le fichier JSON"""
        try:
            data = {email: user.to_dict() for email, user in self._users.items()}
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def create_user(self, email: str, username: str, password: str) -> Optional[User]:
        """Crée un nouvel utilisateur"""
        if email in self._users:
            return None
        
        user = User(email=email, username=username)
        user.set_password(password)
        user.generate_verification_token()
        
        self._users[email] = user
        
        if self._save_users():
            return user
        return None
    
    def get_user(self, email: str) -> Optional[User]:
        """Récupère un utilisateur par email"""
        return self._users.get(email)
    
    def verify_user(self, email: str, token: str) -> bool:
        """Vérifie un utilisateur avec son token"""
        user = self.get_user(email)
        if user and user.verification_token == token:
            user.verify_account()
            return self._save_users()
        return False
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authentifie un utilisateur"""
        user = self.get_user(email)
        if user and user.check_password(password):
            user.update_last_login()
            self._save_users()
            return user
        return None
    
    def get_all_users(self) -> Dict[str, User]:
        """Retourne tous les utilisateurs"""
        return self._users.copy()
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques des utilisateurs"""
        total_users = len(self._users)
        verified_users = sum(1 for user in self._users.values() if user.is_verified)
        
        return {
            'total_users': total_users,
            'verified_users': verified_users,
            'unverified_users': total_users - verified_users
        }
