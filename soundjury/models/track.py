"""
Modèles pour les pistes musicales
"""
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Track:
    """Modèle de base pour une piste musicale"""
    id: str
    title: str
    artist: str
    album: Optional[str] = None
    duration: Optional[str] = None
    image_url: Optional[str] = None
    preview_url: Optional[str] = None
    deezer_id: Optional[str] = None
    genres: Optional[List[str]] = None
    # Champs pour les statistiques de notation
    avg_rating: Optional[float] = 0.0
    rating_count: Optional[int] = 0
    user_rating: Optional[int] = None
    
    def to_dict(self) -> Dict:
        """Convertit la piste en dictionnaire"""
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'duration': self.duration,
            'image_url': self.image_url,
            'preview_url': self.preview_url,
            'deezer_id': self.deezer_id,
            'genres': self.genres or [],
            'avg_rating': self.avg_rating,
            'rating_count': self.rating_count,
            'user_rating': self.user_rating
        }
