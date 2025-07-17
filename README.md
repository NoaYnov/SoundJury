# SoundJury

SoundJury est une application web légère permettant de rechercher de la musique et d'afficher des informations enrichies (genres, durée, date de sortie, plateformes disponibles, extrait audio).  
Elle s'inspire du concept de Letterboxd mais appliqué à l'univers musical.

## Fonctionnalités

- Recherche de titres via Spotify
- Affichage des pochettes, artistes et plateformes (Spotify, Deezer, YouTube)
- Détails supplémentaires chargés dynamiquement via AJAX :
  - Genres musicaux
  - Durée
  - Date de sortie
  - Extrait audio (si disponible)
- Interface simple, responsive et interactive
- Clic sur la carte pour afficher/masquer les détails

## Installation

1. **Cloner le projet** :
   ```bash
   git clone https://github.com/votre-utilisateur/soundjury.git
   cd soundjury
   ```

2. **Créer un environnement virtuel (optionnel mais recommandé)** :
   ```bash
   python -m venv venv
   source venv/bin/activate   # ou venv\Scripts\activate sous Windows
   ```

3. **Installer les dépendances** :
   ```bash
   pip install flask
   ```

4. **Lancer le serveur** :
   ```bash
   python app.py
   ```

5. Ouvrir votre navigateur à l'adresse :  
   [http://localhost:5000](http://localhost:5000)

## Architecture

```
soundjury/
├── app.py                # Serveur principal Flask
├── music_api.py          # Logique de récupération d'informations musicales
├── templates/
│   └── index.html        # Interface utilisateur (HTML + JS intégré)
```

## Limitations

- L’extrait audio dépend de la disponibilité (via Deezer uniquement pour l’instant).
- Les résultats sont limités à 5 pour éviter les ralentissements (modifiable).
- Les données de genre sont parfois incomplètes selon les API disponibles.

## Améliorations possibles

- Intégration d’un système de notation utilisateur
- Comptes et favoris
- Filtres par genre/artiste/durée
- Suggestions musicales basées sur les goûts

---

# SoundJury (EN)

SoundJury is a lightweight web app to search music tracks and display enriched information such as genres, duration, release date, and platform links.  
It is inspired by the Letterboxd model, applied to the world of music.

## Features

- Track search using Spotify API
- Display album art, artist, and platform links (Spotify, Deezer, YouTube)
- On-demand details via AJAX:
  - Music genres
  - Duration
  - Release date
  - Preview audio (if available)
- Clean, responsive UI
- Click on track card to toggle details

## Installation

1. **Clone the project**:
   ```bash
   git clone https://github.com/your-user/soundjury.git
   cd soundjury
   ```

2. **(Optional) Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate   # or venv\Scripts\activate on Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install flask
   ```

4. **Run the server**:
   ```bash
   python app.py
   ```

5. Open your browser at:  
   [http://localhost:5000](http://localhost:5000)

## Structure

```
soundjury/
├── app.py                # Main Flask server
├── music_api.py          # Music data logic
├── templates/
│   └── index.html        # Front-end template
```

## Limitations

- Preview audio is only available if Deezer provides it.
- Result limit is set to 5 for performance (adjustable).
- Genre data may be incomplete depending on the API.

## Future improvements

- User rating system
- User accounts and favorites
- Filters by genre/artist/duration
- Personalized music suggestions
