
# SPOTIPY_CLIENT_ID = "daec6d9a79f942dd8c6aa6f1e01864a2"
# SPOTIPY_CLIENT_SECRET = "2ea349c16553457fb31a3dfccb8d9a53"


import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


SPOTIPY_CLIENT_ID = "daec6d9a79f942dd8c6aa6f1e01864a2"
SPOTIPY_CLIENT_SECRET = "2ea349c16553457fb31a3dfccb8d9a53"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET
))

def format_duration(duration_ms):
    """Convertit une durée en millisecondes en format MM:SS"""
    if not duration_ms:
        return "N/A"
    
    seconds = duration_ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}:{seconds:02d}"
def search_deezer(artist, title):
    try:
        query = f"{artist} {title}"
        r = requests.get(f"https://api.deezer.com/search?q={query}")
        data = r.json()
        if data.get("data"):
            d = data["data"][0]
            return {
                "deezer_url": d["link"],
                "preview_url": d.get("preview"),
                "duration": d.get("duration")
            }
    except Exception as e:
        print("Erreur Deezer:", e)
    return {}
def search_musicbrainz(artist, title):
    try:
        response = requests.get(
            "https://musicbrainz.org/ws/2/recording/",
            params={
                "query": f'artist:"{artist}" AND recording:"{title}"',
                "fmt": "json",
                "limit": 1
            },
            headers={"User-Agent": "SoundJuryApp/1.0 (contact@example.com)"}
        )
        data = response.json()
        if data.get("recordings"):
            rec = data["recordings"][0]
            return {
                "release_date": rec.get("first-release-date"),
                "mbid": rec.get("id")
            }
    except Exception as e:
        print("Erreur MusicBrainz:", e)
    return {}

def get_fast_tracks(query, limit=10):
    results = sp.search(q=query, type='track', limit=limit)
    tracks = []

    for item in results['tracks']['items']:
        artist = item['artists'][0]['name']
        title = item['name']
        image = item['album']['images'][0]['url']
        artist_id = item['artists'][0]['id']

        # Recherche Deezer directe
        deezer_info = search_deezer(artist, title)

        track = {
            "name": title,  # Changé de "title" à "name" pour correspondre au template
            "title": title,  # Gardé pour compatibilité
            "artist": artist,
            "image": image,
            "spotify_url": item['external_urls']['spotify'],
            "deezer_url": deezer_info.get("deezer_url"),
            "youtube_url": f"https://www.youtube.com/results?search_query={artist}+{title}",
            "spotify_id": item['id'],
            "artist_id": artist_id,
            "id": item['id'],  # Ajouté pour l'identifiant unique
            "album": item['album']['name'],  # Ajouté le nom de l'album
            "duration": format_duration(item.get('duration_ms', 0))  # Formatage de la durée
        }

        tracks.append(track)

    return tracks

def get_artist_genres(artist_id):
    data = sp.artist(artist_id)
    return data.get("genres", [])

import requests

def get_full_track_data(artist, title, artist_id=None):
    result = {
        "artist": artist,
        "title": title,
        "album": "N/A",
        "year": "N/A", 
        "duration": "N/A",
        "genres": [],
        "deezer_url": None,
        "preview_url": None
    }

    try:
        # Construire la requête de recherche
        query = f"{artist} {title}"
        search_url = f"https://api.deezer.com/search?q={requests.utils.quote(query)}"
        print("Recherche Deezer:", search_url)
        response = requests.get(search_url)
        response.raise_for_status()
        data = response.json()

        if data.get("data"):
            track = data["data"][0]  # premier résultat trouvé
            duration_seconds = track.get("duration", 0)
            formatted_duration = f"{duration_seconds // 60}:{duration_seconds % 60:02d}" if duration_seconds else "N/A"
            
            result.update({
                "duration": formatted_duration,
                "deezer_url": track.get("link"),
                "preview_url": track.get("preview"),
                "album": track.get("album", {}).get("title", "N/A")
            })

            # Obtenir plus d'infos via track ID
            track_id = track.get("id")
            if track_id:
                detail_url = f"https://api.deezer.com/track/{track_id}"
                detail_resp = requests.get(detail_url)
                detail_resp.raise_for_status()
                detail_data = detail_resp.json()

                release_date = detail_data.get("release_date")
                if release_date:
                    result["year"] = release_date.split("-")[0]  # Extraire l'année

                # Récupérer le genre si disponible
                genre_id = detail_data.get("genre_id")
                if genre_id:
                    genre_url = f"https://api.deezer.com/genre/{genre_id}"
                    genre_resp = requests.get(genre_url)
                    if genre_resp.status_code == 200:
                        genre_data = genre_resp.json()
                        result["genres"] = [genre_data.get("name")]

    except Exception as e:
        print("Erreur dans get_full_track_data:", e)

    return result


def get_trending_tracks(limit=10):
    try:
        response = requests.get(f"https://api.deezer.com/chart/0/tracks?limit={limit}")
        data = response.json()
        tracks = []
        for t in data.get("data", []):
            duration_seconds = t.get("duration", 0)
            formatted_duration = f"{duration_seconds // 60}:{duration_seconds % 60:02d}" if duration_seconds else "N/A"
            
            tracks.append({
                "name": t["title"],  # Utilisé dans le template
                "title": t["title"],  # Compatibilité
                "artist": t["artist"]["name"],
                "album": t["album"]["title"],
                "image": t["album"]["cover_medium"],
                "duration": formatted_duration,
                "spotify_url": None,
                "deezer_url": t["link"],
                "id": str(t["id"]),
                "artist_id": None  # Pas d'artist_id disponible depuis Deezer charts
            })
        return tracks
    except Exception as e:
        print("Erreur Deezer:", e)
        return []
