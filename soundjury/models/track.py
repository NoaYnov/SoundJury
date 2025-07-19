"""
Modèle Track - Gestion des morceaux musicaux
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class Track:
    """Modèle pour représenter un morceau musical"""
    
    title: str
    artist: str
    album: str = ""
    duration: str = ""
    image: str = ""
    spotify_url: str = ""
    youtube_url: str = ""
    deezer_url: str = ""
    id: str = ""
    artist_id: str = ""
    source: str = ""
    genres: List[str] = None
    year: int = None
    release_date: str = ""
    preview_url: str = ""
    avg_rating: float = 0.0
    rating_count: int = 0
    
    def __post_init__(self):
        if self.genres is None:
            self.genres = []
    
    def get_track_id(self) -> str:
        """Génère un ID unique pour le morceau"""
        return f"{self.artist}_{self.title}".lower().replace(" ", "_")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le morceau en dictionnaire"""
        return {
            'title': self.title,
            'name': self.title,  # Alias pour compatibilité
            'artist': self.artist,
            'album': self.album,
            'duration': self.duration,
            'image': self.image,
            'spotify_url': self.spotify_url,
            'youtube_url': self.youtube_url,
            'deezer_url': self.deezer_url,
            'id': self.id,
            'artist_id': self.artist_id,
            'source': self.source,
            'genres': self.genres,
            'year': self.year,
            'release_date': self.release_date,
            'preview_url': self.preview_url,
            'avg_rating': self.avg_rating,
            'rating_count': self.rating_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Track':
        """Crée un morceau à partir d'un dictionnaire"""
        return cls(
            title=data.get('title', data.get('name', '')),
            artist=data.get('artist', ''),
            album=data.get('album', ''),
            duration=data.get('duration', ''),
            image=data.get('image', ''),
            spotify_url=data.get('spotify_url', ''),
            youtube_url=data.get('youtube_url', ''),
            deezer_url=data.get('deezer_url', ''),
            id=data.get('id', ''),
            artist_id=data.get('artist_id', ''),
            source=data.get('source', ''),
            genres=data.get('genres', []),
            year=data.get('year'),
            release_date=data.get('release_date', ''),
            preview_url=data.get('preview_url', '')
        )
    
    def __str__(self) -> str:
        return f"{self.artist} - {self.title}"
    
    def __repr__(self) -> str:
        return f"<Track {self.artist} - {self.title}>"

class TrackDetails:
    """Classe pour les détails étendus d'un morceau"""
    
    def __init__(self, track: Track):
        self.track = track
        self.rating_info = None
        self.user_rating = None
        self.user_has_rated = False
    
    def set_rating_info(self, average: float, count: int, user_rating: int = None):
        """Définit les informations de notation"""
        self.rating_info = {
            'average': average,
            'count': count
        }
        if user_rating is not None:
            self.user_rating = user_rating
            self.user_has_rated = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire avec toutes les informations"""
        result = self.track.to_dict()
        
        if self.rating_info:
            result['rating_info'] = self.rating_info
            result['average'] = self.rating_info['average']
            result['count'] = self.rating_info['count']
        
        if self.user_has_rated:
            result['user_rating'] = self.user_rating
            result['user_has_rated'] = True
        
        return result
