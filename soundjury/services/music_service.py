"""
Service de gestion des APIs musicales
"""
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List, Dict, Any, Optional
from models.track import Track, TrackDetails
from config import Config

class MusicService:
    """Service unifié pour les APIs musicales"""
    
    def __init__(self, config: Config):
        self.config = config
        self.sp = self._init_spotify()
    
    def _init_spotify(self) -> Optional[spotipy.Spotify]:
        """Initialise le client Spotify"""
        try:
            if self.config.SPOTIFY_CLIENT_ID and self.config.SPOTIFY_CLIENT_SECRET:
                client_credentials_manager = SpotifyClientCredentials(
                    client_id=self.config.SPOTIFY_CLIENT_ID,
                    client_secret=self.config.SPOTIFY_CLIENT_SECRET
                )
                return spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        except Exception as e:
            print(f"Erreur initialisation Spotify: {e}")
        return None
    
    def get_trending_tracks(self, limit: int = 10) -> List[Track]:
        """Récupère les morceaux français les plus écoutés"""
        try:
            tracks = []
            
            # 1. Récupérer les morceaux français depuis Deezer
            tracks.extend(self._get_deezer_trending_fr(limit))
            
            # 2. Compléter avec Spotify si nécessaire
            if len(tracks) < limit and self.sp:
                remaining = limit - len(tracks)
                tracks.extend(self._get_spotify_trending_fr(remaining))
            
            # 3. Fallback avec le top global Deezer
            if len(tracks) < limit:
                remaining = limit - len(tracks)
                tracks.extend(self._get_deezer_trending_global(remaining))
            
            return tracks[:limit]
            
        except Exception as e:
            print(f"Erreur get_trending_tracks: {e}")
            return []
    
    def _get_deezer_trending_fr(self, limit: int) -> List[Track]:
        """Récupère les morceaux français populaires depuis Deezer"""
        try:
            response = requests.get(f"https://api.deezer.com/chart/116/tracks?limit={limit}")
            
            if response.status_code != 200:
                return []
                
            data = response.json()
            tracks = []
            
            for t in data.get("data", []):
                track = self._create_track_from_deezer(t, "deezer_fr")
                if track:
                    tracks.append(track)
            
            return tracks
            
        except Exception as e:
            print(f"Erreur Deezer France: {e}")
            return []
    
    def _get_deezer_trending_global(self, limit: int) -> List[Track]:
        """Récupère les morceaux populaires globaux depuis Deezer"""
        try:
            response = requests.get(f"https://api.deezer.com/chart/0/tracks?limit={limit}")
            
            if response.status_code != 200:
                return []
                
            data = response.json()
            tracks = []
            
            for t in data.get("data", []):
                track = self._create_track_from_deezer(t, "deezer_global")
                if track:
                    tracks.append(track)
            
            return tracks
            
        except Exception as e:
            print(f"Erreur Deezer Global: {e}")
            return []
    
    def _get_spotify_trending_fr(self, limit: int) -> List[Track]:
        """Récupère les morceaux français populaires depuis Spotify"""
        try:
            if not self.sp:
                return []
                
            playlists_queries = [
                "Top France",
                "Hits France", 
                "Rap français",
                "Chanson française",
                "French Pop"
            ]
            
            tracks = []
            seen_tracks = set()
            
            for query in playlists_queries:
                if len(tracks) >= limit:
                    break
                
                try:
                    results = self.sp.search(q=query, type='playlist', market='FR', limit=5)
                    
                    for playlist in results['playlists']['items']:
                        if len(tracks) >= limit:
                            break
                        
                        playlist_tracks = self.sp.playlist_tracks(
                            playlist['id'],
                            market='FR',
                            limit=min(20, limit - len(tracks))
                        )
                        
                        for item in playlist_tracks['items']:
                            if len(tracks) >= limit:
                                break
                            
                            if not item['track'] or not item['track']['artists']:
                                continue
                            
                            track = self._create_track_from_spotify(item['track'], "spotify_fr")
                            if track:
                                track_key = f"{track.artist}_{track.title}"
                                if track_key not in seen_tracks:
                                    tracks.append(track)
                                    seen_tracks.add(track_key)
                                    
                except Exception as e:
                    print(f"Erreur playlist Spotify: {e}")
                    continue
            
            return tracks
            
        except Exception as e:
            print(f"Erreur Spotify France: {e}")
            return []
    
    def _create_track_from_deezer(self, data: Dict[str, Any], source: str) -> Optional[Track]:
        """Crée un Track à partir des données Deezer"""
        try:
            duration_seconds = data.get("duration", 0)
            formatted_duration = f"{duration_seconds // 60}:{duration_seconds % 60:02d}" if duration_seconds else "N/A"
            
            artist_name = data["artist"]["name"]
            track_title = data["title"]
            search_query = f"{artist_name} {track_title}".replace(" ", "+")
            
            return Track(
                title=track_title,
                artist=artist_name,
                album=data["album"]["title"],
                duration=formatted_duration,
                image=data["album"]["cover_medium"],
                spotify_url=f"https://open.spotify.com/search/{search_query}",
                youtube_url=f"https://music.youtube.com/search?q={search_query}",
                deezer_url=data["link"],
                id=str(data["id"]),
                source=source
            )
            
        except Exception as e:
            print(f"Erreur création track Deezer: {e}")
            return None
    
    def _create_track_from_spotify(self, data: Dict[str, Any], source: str) -> Optional[Track]:
        """Crée un Track à partir des données Spotify"""
        try:
            duration_ms = data.get('duration_ms', 0)
            formatted_duration = f"{duration_ms // 60000}:{(duration_ms % 60000) // 1000:02d}" if duration_ms else "N/A"
            
            artist_name = data['artists'][0]['name']
            track_title = data['name']
            search_query = f"{artist_name} {track_title}".replace(" ", "+")
            
            return Track(
                title=track_title,
                artist=artist_name,
                album=data['album']['name'],
                duration=formatted_duration,
                image=data['album']['images'][0]['url'] if data['album']['images'] else "",
                spotify_url=data['external_urls']['spotify'],
                youtube_url=f"https://music.youtube.com/search?q={search_query}",
                deezer_url=f"https://www.deezer.com/search/{search_query}",
                id=data['id'],
                artist_id=data['artists'][0]['id'],
                source=source
            )
            
        except Exception as e:
            print(f"Erreur création track Spotify: {e}")
            return None
    
    def search_tracks(self, query: str, limit: int = 20) -> List[Track]:
        """Recherche des morceaux"""
        try:
            tracks = []
            
            # Recherche Spotify
            if self.sp:
                tracks.extend(self._search_spotify(query, limit // 2))
            
            # Recherche Deezer
            tracks.extend(self._search_deezer(query, limit // 2))
            
            return tracks[:limit]
            
        except Exception as e:
            print(f"Erreur recherche: {e}")
            return []
    
    def _search_spotify(self, query: str, limit: int) -> List[Track]:
        """Recherche sur Spotify"""
        try:
            if not self.sp:
                return []
                
            results = self.sp.search(q=query, type='track', limit=limit)
            tracks = []
            
            for track_data in results['tracks']['items']:
                track = self._create_track_from_spotify(track_data, "spotify_search")
                if track:
                    tracks.append(track)
            
            return tracks
            
        except Exception as e:
            print(f"Erreur recherche Spotify: {e}")
            return []
    
    def _search_deezer(self, query: str, limit: int) -> List[Track]:
        """Recherche sur Deezer"""
        try:
            response = requests.get(f"https://api.deezer.com/search/track?q={query}&limit={limit}")
            
            if response.status_code != 200:
                return []
                
            data = response.json()
            tracks = []
            
            for track_data in data.get("data", []):
                track = self._create_track_from_deezer(track_data, "deezer_search")
                if track:
                    tracks.append(track)
            
            return tracks
            
        except Exception as e:
            print(f"Erreur recherche Deezer: {e}")
            return []
    
    def get_track_details(self, artist: str, title: str, artist_id: str = None) -> Dict[str, Any]:
        """Récupère les détails d'un morceau"""
        try:
            details = {}
            
            # Essayer d'abord avec Spotify
            if self.sp:
                spotify_details = self._get_spotify_track_details(artist, title, artist_id)
                if spotify_details:
                    details.update(spotify_details)
            
            # Compléter avec Deezer si nécessaire
            if not details:
                deezer_details = self._get_deezer_track_details(artist, title)
                if deezer_details:
                    details.update(deezer_details)
            
            return details
            
        except Exception as e:
            print(f"Erreur détails morceau: {e}")
            return {}
    
    def _get_spotify_track_details(self, artist: str, title: str, artist_id: str = None) -> Optional[Dict[str, Any]]:
        """Récupère les détails depuis Spotify"""
        try:
            if not self.sp:
                return None
                
            # Rechercher le morceau
            query = f"artist:{artist} track:{title}"
            results = self.sp.search(q=query, type='track', limit=1)
            
            if not results['tracks']['items']:
                return None
            
            track = results['tracks']['items'][0]
            
            # Récupérer les détails de l'album
            album_id = track['album']['id']
            album = self.sp.album(album_id)
            
            # Récupérer les détails de l'artiste
            artist_details = self.sp.artist(track['artists'][0]['id'])
            
            return {
                'duration': f"{track['duration_ms'] // 60000}:{(track['duration_ms'] % 60000) // 1000:02d}",
                'album': track['album']['name'],
                'release_date': track['album']['release_date'],
                'year': int(track['album']['release_date'][:4]) if track['album']['release_date'] else None,
                'genres': artist_details.get('genres', []),
                'preview_url': track.get('preview_url'),
                'popularity': track.get('popularity', 0)
            }
            
        except Exception as e:
            print(f"Erreur détails Spotify: {e}")
            return None
    
    def _get_deezer_track_details(self, artist: str, title: str) -> Optional[Dict[str, Any]]:
        """Récupère les détails depuis Deezer"""
        try:
            response = requests.get(f"https://api.deezer.com/search/track?q={artist} {title}&limit=1")
            
            if response.status_code != 200:
                return None
                
            data = response.json()
            if not data.get("data"):
                return None
            
            track = data["data"][0]
            
            return {
                'duration': f"{track['duration'] // 60}:{track['duration'] % 60:02d}",
                'album': track['album']['title'],
                'release_date': track.get('release_date', ''),
                'year': None,
                'genres': [],
                'preview_url': track.get('preview'),
                'popularity': track.get('rank', 0)
            }
            
        except Exception as e:
            print(f"Erreur détails Deezer: {e}")
            return None
