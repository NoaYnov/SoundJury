
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

def get_fast_tracks(query, limit=5):
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
            "title": title,
            "artist": artist,
            "image": image,
            "spotify_url": item['external_urls']['spotify'],
            "youtube_url": f"https://www.youtube.com/results?search_query={artist}+{title}",
            "spotify_id": item['id'],
            "artist_id": artist_id,
            "deezer_url": deezer_info.get("deezer_url")  # <-- Important
        }

        tracks.append(track)

    return tracks

def get_artist_genres(artist_id):
    data = sp.artist(artist_id)
    return data.get("genres", [])

def get_full_track_data(artist, title, artist_id):
    result = {
        "deezer_url": None,
        "preview_url": None,
        "release_date": None,
        "genres": [],
        "duration": None
    }

    # Deezer
    d = search_deezer(artist, title)
    result.update(d)

    # MusicBrainz
    m = search_musicbrainz(artist, title)
    result.update(m)

    # Spotify genres
    result["genres"] = get_artist_genres(artist_id)

    return result