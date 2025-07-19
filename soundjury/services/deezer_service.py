"""
Service de musique utilisant l'API Deezer
"""
import requests
import json
from typing import List, Dict, Optional
from urllib.parse import quote
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.track import Track

class DeezerMusicService:
    """Service pour interagir avec l'API Deezer"""
    
    def __init__(self):
        self.base_url = "https://api.deezer.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SoundJury/1.0'
        })
    
    def _make_request(self, endpoint: str, params: dict = None) -> dict:
        """Effectue une requête à l'API Deezer"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erreur API Deezer: {e}")
            return {}
    
    def get_trending_tracks(self, limit: int = 10) -> List[Track]:
        """Récupère les morceaux tendance depuis le top France"""
        try:
            # Utiliser le chart France de Deezer
            data = self._make_request("/chart/0/tracks", {"limit": limit})
            
            if not data or 'data' not in data:
                return self._get_mock_tracks(limit)
            
            tracks = []
            for track_data in data['data']:
                track = Track(
                    id=str(track_data['id']),
                    title=track_data['title'],
                    artist=track_data['artist']['name'],
                    album=track_data['album']['title'] if track_data.get('album') else '',
                    duration=self.format_duration(track_data.get('duration', 0)),
                    image=track_data['album']['cover_medium'] if track_data.get('album') else track_data['artist'].get('picture_medium', ''),
                    youtube_url=self._get_youtube_url(track_data['title'], track_data['artist']['name']),
                    deezer_url=track_data.get('link', ''),
                    preview_url=track_data.get('preview', ''),  # Ajout de l'URL de prévisualisation
                    spotify_url='',
                    artist_id=str(track_data['artist']['id'])
                )
                tracks.append(track)
            
            return tracks
        except Exception as e:
            print(f"Erreur lors de la récupération des tendances: {e}")
            return self._get_mock_tracks(limit)
    
    def search_tracks(self, query: str, limit: int = 20) -> List[Track]:
        """Recherche des morceaux sur Deezer"""
        try:
            # Nettoyer et encoder la requête
            clean_query = query.strip()
            if not clean_query:
                return []
            
            params = {
                'q': clean_query,
                'limit': limit
            }
            
            data = self._make_request("/search/track", params)
            
            if not data or 'data' not in data:
                return self._search_mock_tracks(query, limit)
            
            tracks = []
            for track_data in data['data']:
                track = Track(
                    id=str(track_data['id']),
                    title=track_data['title'],
                    artist=track_data['artist']['name'],
                    album=track_data['album']['title'] if track_data.get('album') else '',
                    duration=self.format_duration(track_data.get('duration', 0)),
                    image=track_data['album']['cover_medium'] if track_data.get('album') else track_data['artist'].get('picture_medium', ''),
                    youtube_url=self._get_youtube_url(track_data['title'], track_data['artist']['name']),
                    deezer_url=track_data.get('link', ''),
                    preview_url=track_data.get('preview', ''),  # Ajout de l'URL de prévisualisation
                    spotify_url='',
                    artist_id=str(track_data['artist']['id'])
                )
                tracks.append(track)
            
            return tracks
        except Exception as e:
            print(f"Erreur lors de la recherche: {e}")
            return self._search_mock_tracks(query, limit)
    
    def get_track_details(self, track_id: str) -> Optional[Track]:
        """Récupère les détails d'un morceau"""
        try:
            data = self._make_request(f"/track/{track_id}")
            
            if not data or 'id' not in data:
                return None
            
            return Track(
                id=str(data['id']),
                title=data['title'],
                artist=data['artist']['name'],
                album=data['album']['title'] if data.get('album') else '',
                duration=self.format_duration(data.get('duration', 0)),
                image=data['album']['cover_medium'] if data.get('album') else data['artist'].get('picture_medium', ''),
                youtube_url=self._get_youtube_url(data['title'], data['artist']['name']),
                deezer_url=data.get('link', ''),
                spotify_url='',
                artist_id=str(data['artist']['id'])
            )
        except Exception as e:
            print(f"Erreur lors de la récupération des détails: {e}")
            return None
    
    def _get_youtube_url(self, title: str, artist: str) -> str:
        """Génère une URL YouTube de recherche"""
        query = f"{title} {artist}"
        encoded_query = quote(query)
        return f"https://www.youtube.com/results?search_query={encoded_query}"
    
    def format_duration(self, seconds: int) -> str:
        """Formate la durée en mm:ss"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"
    
    def _get_mock_tracks(self, limit: int) -> List[Track]:
        """Retourne des données de test en cas d'erreur API"""
        mock_data = [
            {
                'id': 'mock_1',
                'title': 'Dernière danse',
                'artist': 'Indila',
                'album': 'Mini World',
                'duration': 215,
                'image': 'https://via.placeholder.com/300x300/1DB954/ffffff?text=DD',
                'youtube_url': 'https://www.youtube.com/results?search_query=Dernière+danse+Indila',
                'deezer_url': ''
            },
            {
                'id': 'mock_2',
                'title': 'Alors on danse',
                'artist': 'Stromae',
                'album': 'Cheese',
                'duration': 205,
                'image': 'https://via.placeholder.com/300x300/FF6B35/ffffff?text=AOD',
                'youtube_url': 'https://www.youtube.com/results?search_query=Alors+on+danse+Stromae',
                'deezer_url': ''
            },
            {
                'id': 'mock_3',
                'title': 'La vie en rose',
                'artist': 'Édith Piaf',
                'album': 'La Vie En Rose',
                'duration': 189,
                'image': 'https://via.placeholder.com/300x300/00D4AA/ffffff?text=LVER',
                'youtube_url': 'https://www.youtube.com/results?search_query=La+vie+en+rose+Édith+Piaf',
                'deezer_url': ''
            },
            {
                'id': 'mock_4',
                'title': 'Tout oublier',
                'artist': 'Angèle ft. Roméo Elvis',
                'album': 'Brol',
                'duration': 193,
                'image': 'https://via.placeholder.com/300x300/F037A5/ffffff?text=TO',
                'youtube_url': 'https://www.youtube.com/results?search_query=Tout+oublier+Angèle',
                'deezer_url': ''
            },
            {
                'id': 'mock_5',
                'title': 'Papaoutai',
                'artist': 'Stromae',
                'album': 'Racine Carrée',
                'duration': 233,
                'image': 'https://via.placeholder.com/300x300/7209B7/ffffff?text=PAP',
                'youtube_url': 'https://www.youtube.com/results?search_query=Papaoutai+Stromae',
                'deezer_url': ''
            }
        ]
        
        tracks = []
        for data in mock_data[:limit]:
            track = Track(
                id=data['id'],
                title=data['title'],
                artist=data['artist'],
                album=data['album'],
                duration=self.format_duration(data['duration']),
                image=data['image'],
                youtube_url=data['youtube_url'],
                deezer_url=data['deezer_url'],
                spotify_url='',
                artist_id=''
            )
            tracks.append(track)
        
        return tracks
    
    def _search_mock_tracks(self, query: str, limit: int) -> List[Track]:
        """Recherche dans les données de test"""
        mock_tracks = self._get_mock_tracks(10)
        results = []
        query_lower = query.lower()
        
        for track in mock_tracks:
            if (query_lower in track.title.lower() or 
                query_lower in track.artist.lower() or
                query_lower in track.album.lower()):
                results.append(track)
        
        # Si aucun résultat, retourner quelques morceaux aléatoires
        if not results:
            results = mock_tracks[:3]
        
        return results[:limit]
    
    def is_authenticated(self) -> bool:
        """Vérifie si le service est authentifié (toujours vrai pour Deezer)"""
        return True
    
    def get_authentication_url(self) -> str:
        """URL d'authentification (non nécessaire pour Deezer API publique)"""
        return ""
    
    def authenticate(self, code: str) -> bool:
        """Authentification (non nécessaire pour Deezer API publique)"""
        return True
