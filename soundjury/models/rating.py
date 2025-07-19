"""
Modèle Rating - Gestion des notations
"""
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from threading import Lock

class Rating:
    """Modèle pour une notation"""
    
    def __init__(self, track_id: str, user_email: str, artist: str, title: str, 
                 rating: int, timestamp: str = None):
        self.track_id = track_id
        self.user_email = user_email
        self.artist = artist
        self.title = title
        self.rating = rating
        self.timestamp = timestamp or datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la notation en dictionnaire"""
        return {
            'track_id': self.track_id,
            'user_email': self.user_email,
            'artist': self.artist,
            'title': self.title,
            'rating': self.rating,
            'timestamp': self.timestamp,
            'count': 1,  # Compatibilité
            'total': self.rating,
            'average': self.rating
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Rating':
        """Crée une notation à partir d'un dictionnaire"""
        return cls(
            track_id=data['track_id'],
            user_email=data['user_email'],
            artist=data['artist'],
            title=data['title'],
            rating=data['rating'],
            timestamp=data.get('timestamp')
        )

class TrackRatingStats:
    """Statistiques de notation pour un morceau"""
    
    def __init__(self, track_id: str, artist: str, title: str):
        self.track_id = track_id
        self.artist = artist
        self.title = title
        self.ratings: List[Rating] = []
        self.voters: List[str] = []
    
    def add_rating(self, rating: Rating) -> bool:
        """Ajoute ou modifie une notation"""
        # Vérifier si l'utilisateur a déjà voté
        existing_rating = next(
            (r for r in self.ratings if r.user_email == rating.user_email), 
            None
        )
        
        if existing_rating:
            # Modifier la notation existante
            existing_rating.rating = rating.rating
            existing_rating.timestamp = rating.timestamp
        else:
            # Ajouter une nouvelle notation
            self.ratings.append(rating)
            self.voters.append(rating.user_email)
        
        return True
    
    def get_average(self) -> float:
        """Calcule la moyenne des notations"""
        if not self.ratings:
            return 0.0
        return round(sum(r.rating for r in self.ratings) / len(self.ratings), 1)
    
    def get_count(self) -> int:
        """Retourne le nombre de votes"""
        return len(self.ratings)
    
    def get_total(self) -> int:
        """Retourne le total des points"""
        return sum(r.rating for r in self.ratings)
    
    def get_user_rating(self, user_email: str) -> Optional[int]:
        """Retourne la notation d'un utilisateur spécifique"""
        for rating in self.ratings:
            if rating.user_email == user_email:
                return rating.rating
        return None
    
    def has_user_rated(self, user_email: str) -> bool:
        """Vérifie si un utilisateur a déjà noté"""
        return user_email in self.voters
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            'track_id': self.track_id,
            'artist': self.artist,
            'title': self.title,
            'count': self.get_count(),
            'total': self.get_total(),
            'average': self.get_average(),
            'voters': self.voters.copy()
        }

class RatingManager:
    """Gestionnaire des notations avec persistance JSON"""
    
    def __init__(self, ratings_file: str):
        self.ratings_file = ratings_file
        self.lock = Lock()
        self._ratings_data = self._load_ratings()
    
    def _load_ratings(self) -> Dict[str, Any]:
        """Charge les données de notation depuis le fichier JSON"""
        try:
            with open(self.ratings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            print(f"Erreur lors du chargement de {self.ratings_file}")
            return {}
    
    def _save_ratings(self) -> bool:
        """Sauvegarde les données de notation"""
        try:
            with open(self.ratings_file, 'w', encoding='utf-8') as f:
                json.dump(self._ratings_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def _get_track_id(self, artist: str, title: str) -> str:
        """Génère un ID unique pour un morceau"""
        return f"{artist}_{title}".lower().replace(" ", "_")
    
    def _get_user_rating_key(self, track_id: str, user_email: str) -> str:
        """Génère une clé unique pour un vote utilisateur"""
        return f"{track_id}_{user_email}".replace("@", "_at_").replace(".", "_dot_")
    
    def add_rating(self, artist: str, title: str, rating: int, user_email: str) -> tuple[bool, str]:
        """Ajoute ou modifie une notation"""
        if not (1 <= rating <= 5):
            return False, "Note invalide (1-5)"
        
        if not user_email:
            return False, "Utilisateur non connecté"
        
        with self.lock:
            track_id = self._get_track_id(artist, title)
            user_rating_key = self._get_user_rating_key(track_id, user_email)
            
            # Vérifier si l'utilisateur a déjà voté
            existing_user_rating = self._ratings_data.get(user_rating_key, {})
            is_update = existing_user_rating.get("count", 0) > 0
            old_rating = existing_user_rating.get("rating", 0) if is_update else 0
            
            # Enregistrer le vote utilisateur
            rating_obj = Rating(track_id, user_email, artist, title, rating)
            self._ratings_data[user_rating_key] = rating_obj.to_dict()
            
            # Mettre à jour les statistiques globales
            current_stats = self._ratings_data.get(track_id, {})
            
            if is_update:
                # Modification d'une note existante
                if current_stats.get("count", 0) > 0:
                    current_stats["total"] = current_stats["total"] - old_rating + rating
                else:
                    current_stats = {
                        "total": rating,
                        "count": 1,
                        "artist": artist,
                        "title": title,
                        "voters": [user_email]
                    }
            else:
                # Nouvelle note
                if current_stats.get("count", 0) > 0:
                    current_stats["total"] += rating
                    current_stats["count"] += 1
                    if "voters" not in current_stats:
                        current_stats["voters"] = []
                    current_stats["voters"].append(user_email)
                else:
                    current_stats = {
                        "total": rating,
                        "count": 1,
                        "artist": artist,
                        "title": title,
                        "voters": [user_email]
                    }
            
            # Calculer la nouvelle moyenne
            current_stats["average"] = round(current_stats["total"] / current_stats["count"], 1)
            
            # Sauvegarder les stats globales
            self._ratings_data[track_id] = current_stats
            
            success = self._save_ratings()
            
            if success:
                message = "Note modifiée avec succès !" if is_update else "Note ajoutée avec succès !"
                return True, message
            else:
                return False, "Erreur de sauvegarde"
    
    def get_rating(self, artist: str, title: str) -> Dict[str, Any]:
        """Récupère les informations de notation pour un morceau"""
        track_id = self._get_track_id(artist, title)
        return self._ratings_data.get(track_id, {})
    
    def get_user_rating(self, artist: str, title: str, user_email: str) -> Optional[int]:
        """Récupère la note d'un utilisateur pour un morceau"""
        if not user_email:
            return None
        
        track_id = self._get_track_id(artist, title)
        user_rating_key = self._get_user_rating_key(track_id, user_email)
        user_rating = self._ratings_data.get(user_rating_key, {})
        
        if user_rating.get("count", 0) > 0:
            return user_rating.get("rating")
        return None
    
    def has_user_rated(self, artist: str, title: str, user_email: str) -> bool:
        """Vérifie si un utilisateur a déjà noté un morceau"""
        return self.get_user_rating(artist, title, user_email) is not None
    
    def get_top_rated_tracks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Récupère les morceaux les mieux notés"""
        # Filtrer les morceaux avec au moins 1 vote
        rated_tracks = [
            {**data, "track_id": track_id}
            for track_id, data in self._ratings_data.items()
            if data.get("count", 0) > 0 and not "_at_" in track_id
        ]
        
        # Trier par moyenne décroissante, puis par nombre de votes
        rated_tracks.sort(key=lambda x: (x.get("average", 0), x.get("count", 0)), reverse=True)
        
        return rated_tracks[:limit]
    
    def get_user_rated_tracks(self, user_email: str) -> List[Dict[str, Any]]:
        """Récupère tous les morceaux notés par un utilisateur"""
        if not user_email:
            return []
        
        user_tracks = []
        email_key = user_email.replace("@", "_at_").replace(".", "_dot_")
        
        for key, data in self._ratings_data.items():
            if f"_{email_key}" in key and data.get("user_email") == user_email:
                track_id = data.get("track_id")
                if track_id:
                    global_stats = self._ratings_data.get(track_id, {})
                    user_tracks.append({
                        "track_id": track_id,
                        "artist": data.get("artist"),
                        "title": data.get("title"),
                        "user_rating": data.get("rating"),
                        "timestamp": data.get("timestamp"),
                        "global_average": global_stats.get("average", 0),
                        "global_count": global_stats.get("count", 0)
                    })
        
        # Trier par timestamp décroissant
        user_tracks.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return user_tracks
    
    def get_all_ratings(self) -> Dict[str, Any]:
        """Retourne toutes les données de notation"""
        return self._ratings_data.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques globales"""
        try:
            track_ratings = {k: v for k, v in self._ratings_data.items() if not "_at_" in k and v.get("count", 0) > 0}
            user_ratings = {k: v for k, v in self._ratings_data.items() if "_at_" in k and v.get("count", 0) > 0}
            
            total_tracks = len(track_ratings)
            total_ratings = len(user_ratings)
            active_users = len(set(rating.get("user_email", "") for rating in user_ratings.values() if rating.get("user_email", "")))
            avg_rating = round(sum(track.get("average", 0) for track in track_ratings.values()) / total_tracks, 1) if total_tracks > 0 else 0
            
            return {
                "total_tracks": total_tracks,
                "total_ratings": total_ratings,
                "active_users": active_users,
                "avg_rating": avg_rating,
                "top_tracks": self.get_top_rated_tracks(5)
            }
        except Exception as e:
            # Retourner des statistiques par défaut en cas d'erreur
            return {
                "total_tracks": 0,
                "total_ratings": 0,
                "active_users": 0,
                "avg_rating": 0,
                "top_tracks": []
            }
