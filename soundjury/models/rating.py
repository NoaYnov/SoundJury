"""
Gestionnaire des notations
"""
from typing import Dict, List, Optional
from datetime import datetime

class RatingManager:
    """Gestionnaire pour les notations de pistes"""
    
    def __init__(self, supabase_service):
        self.supabase_service = supabase_service
    
    def add_rating(self, user_id: str, track_id: str, rating: int, comment: str = None) -> Dict:
        """Ajouter ou mettre à jour une notation"""
        return self.supabase_service.add_rating_by_id(user_id, track_id, rating, comment)
    
    def get_user_rating(self, user_id: str, track_id: str) -> Optional[Dict]:
        """Récupérer la notation d'un utilisateur pour une piste"""
        return self.supabase_service.get_user_rating_by_id(user_id, track_id)
    
    def get_track_ratings(self, track_id: str) -> List[Dict]:
        """Récupérer toutes les notations d'une piste"""
        return self.supabase_service.get_track_ratings(track_id)
    
    def get_user_ratings(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Récupérer toutes les notations d'un utilisateur"""
        return self.supabase_service.get_user_ratings(user_id, limit)
    
    def validate_rating(self, rating: int) -> bool:
        """Valider qu'une note est dans la plage correcte"""
        return 1 <= rating <= 5
