# 🎵 SoundJury

Une application web moderne pour découvrir, noter et partager de la musique tendance.

## 🚀 Fonctionnalités

- 🎼 **Découverte musicale** : Explorez les morceaux les plus populaires
- ⭐ **Système de notation** : Notez vos morceaux préférés de 1 à 5 étoiles
- 🔍 **Recherche avancée** : Trouvez des artistes, albums et morceaux
- 🎧 **Extraits audio** : Écoutez des prévisualisations de 30 secondes
- 📱 **Interface responsive** : Expérience optimisée sur mobile et desktop
- 👥 **Communauté** : Partagez vos goûts musicaux avec d'autres utilisateurs

## 🏗️ Architecture

```
SoundJury/
├── soundjury/           # Code principal de l'application
│   ├── models/          # Modèles de données
│   ├── services/        # Services (API Deezer, authentification)
│   ├── templates/       # Templates HTML
│   ├── static/          # Fichiers statiques (CSS, JS, images)
│   ├── utils/           # Utilitaires (base de données, email)
│   └── data/            # Données persistantes
├── tests/               # Tests unitaires et d'intégration
├── scripts/             # Scripts utilitaires
├── docs/                # Documentation
└── requirements.txt     # Dépendances Python
```

## 🛠️ Installation

1. **Clonez le repository**
   ```bash
   git clone https://github.com/NoaYnov/SoundJury.git
   cd SoundJury
   ```

2. **Installez les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**
   - Copiez `.env.example` vers `.env`
   - Configurez vos clés API Spotify/Deezer
   - Configurez votre serveur email (optionnel)

4. **Lancez l'application**
   ```bash
   cd soundjury
   python app.py
   ```

## 📚 Documentation

- [Guide de démarrage](docs/DEMARRAGE_RAPIDE.md)
- [Configuration de la base de données](docs/DATABASE_SETUP.md)
- [Configuration email](docs/EMAIL_SETUP.md)
- [Guide responsive](docs/GUIDE_RESPONSIVE.md)

## 🧪 Tests

Les tests sont organisés dans le dossier `tests/`. Pour les exécuter :

```bash
python -m pytest tests/
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Consultez nos [guidelines de contribution](docs/CONTRIBUTING.md).

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🎯 Roadmap

- [ ] Intégration API Spotify complète
- [ ] Recommandations personnalisées
- [ ] Playlists collaboratives
- [ ] Mode hors ligne
- [ ] Application mobile native

---

Développé avec ❤️ par [NoaYnov](https://github.com/NoaYnov)
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
