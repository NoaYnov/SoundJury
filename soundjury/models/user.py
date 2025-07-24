"""
Modèle utilisateur pour Flask-Login
"""
from flask_login import UserMixin
from typing import Optional, Dict

class User(UserMixin):
    """Classe utilisateur pour Flask-Login"""
    
    def __init__(self, user_data: Dict = None, **kwargs):
        # Supporter les deux formats : User(dict) et User(id=..., email=...)
        if user_data is not None:
            data = user_data
        else:
            data = kwargs
            
        self.id = data.get('id')
        self.email = data.get('email')
        self.username = data.get('username')
        self.full_name = data.get('full_name')
        self.avatar_url = data.get('avatar_url')
        self.bio = data.get('bio')
        self.location = data.get('location')
        self.favorite_genres = data.get('favorite_genres', [])
        self.is_verified = data.get('is_verified', False)
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
    
    def get_id(self) -> str:
        """Retourne l'ID de l'utilisateur pour Flask-Login"""
        return str(self.id)
    
    def is_authenticated(self) -> bool:
        """Retourne True si l'utilisateur est authentifié"""
        return True
    
    def is_active(self) -> bool:
        """Retourne True si l'utilisateur est actif"""
        return True
    
    def is_anonymous(self) -> bool:
        """Retourne False car ce n'est pas un utilisateur anonyme"""
        return False
    
    def to_dict(self) -> Dict:
        """Convertit l'utilisateur en dictionnaire"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'full_name': self.full_name,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'location': self.location,
            'favorite_genres': self.favorite_genres,
            'is_verified': self.is_verified,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }