"""
SoundJury - Application principale
Architecture professionnelle avec classes et services
"""
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env du dossier parent
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

# Configuration
from config import config

# Modèles
from models.user import User
from models.track import Track, TrackDetails
from models.rating import RatingManager

# Services
from services.auth_service import AuthService
from services.deezer_service import DeezerMusicService
from services.supabase_service import SupabaseService

# Utilitaires
from utils import EmailService

class SoundJuryApp:
    """Application principale SoundJury"""
    
    def __init__(self, config_name='default'):
        self.app = Flask(__name__)
        self.config = config[config_name]
        self.config.init_app(self.app)
        
        # Initialiser les services
        self.supabase_service = SupabaseService()
        self.auth_service = AuthService(self.config)
        self.music_service = DeezerMusicService()
        # Remplacer RatingManager par le service Supabase
        # self.rating_manager = RatingManager(self.config.RATINGS_FILE)
        
        # Configurer Flask-Login
        self.login_manager = LoginManager()
        self.login_manager.init_app(self.app)
        self.login_manager.login_view = 'login'
        self.login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
        
        # Configurer les routes
        self._setup_routes()
        self._setup_login_manager()
    
    def _setup_login_manager(self):
        """Configure Flask-Login"""
        @self.login_manager.user_loader
        def load_user(user_email):
            return self.auth_service.get_user(user_email)
    
    def _setup_routes(self):
        """Configure toutes les routes de l'application"""
        
        @self.app.route("/")
        def home():
            """Page d'accueil avec morceaux tendance"""
            tracks = self.music_service.get_trending_tracks(limit=10)
            stats = self.supabase_service.get_global_stats()
            
            # Ajouter les informations de notation aux morceaux
            tracks_with_ratings = []
            for track in tracks:
                # Enrichir le track avec les données de notation
                rating_info = self.supabase_service.get_track_stats(track.artist, track.title)
                if rating_info:
                    track.avg_rating = rating_info.get('average_rating', 0)
                    track.rating_count = rating_info.get('total_ratings', 0)
                else:
                    track.avg_rating = 0
                    track.rating_count = 0
                
                # Ajouter la note de l'utilisateur actuel si connecté
                if current_user.is_authenticated:
                    user_rating = self.supabase_service.get_user_rating(
                        current_user.email, track.artist, track.title
                    )
                    track.user_rating = user_rating if user_rating else 0
                else:
                    track.user_rating = 0
                
                tracks_with_ratings.append(track)
            
            return render_template("home.html", tracks=tracks_with_ratings, stats=stats)
        
        @self.app.route("/search", methods=["GET", "POST"])
        def search():
            """Page de recherche"""
            query = ""
            tracks = []
            
            if request.method == "POST":
                query = request.form.get("query", "").strip()
                if query:
                    search_results = self.music_service.search_tracks(query, limit=20)
                    
                    # Ajouter les informations de notation
                    for track in search_results:
                        rating_info = self.supabase_service.get_track_stats(track.artist, track.title)
                        if rating_info:
                            track.avg_rating = rating_info.get('average_rating', 0)
                            track.rating_count = rating_info.get('total_ratings', 0)
                        tracks.append(track)
            
            return render_template("index.html", query=query, tracks=tracks)
        
        @self.app.route("/details", methods=["POST"])
        def details():
            """API pour récupérer les détails d'un morceau"""
            try:
                data = request.get_json()
                artist = data.get("artist")
                title = data.get("title")
                artist_id = data.get("artist_id")
                
                if not artist or not title:
                    return jsonify({"error": "Artiste et titre requis"}), 400
                
                # Récupérer les détails du morceau
                track_details = self.music_service.get_track_details(artist, title, artist_id)
                
                # Ajouter les informations de notation
                rating_info = self.supabase_service.get_track_stats(artist, title)
                if rating_info:
                    track_details['average'] = rating_info.get('average_rating', 0)
                    track_details['count'] = rating_info.get('total_ratings', 0)
                
                # Ajouter la note de l'utilisateur si connecté
                if current_user.is_authenticated:
                    user_rating = self.supabase_service.get_user_rating(current_user.email, artist, title)
                    if user_rating:
                        track_details['user_rating'] = user_rating
                        track_details['user_has_rated'] = True
                
                return jsonify(track_details)
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/rate", methods=["POST"])
        @login_required
        def rate():
            """API pour noter un morceau"""
            try:
                if not current_user.is_verified:
                    return jsonify({"success": False, "error": "Compte non vérifié"}), 403
                
                data = request.get_json()
                artist = data.get("artist")
                title = data.get("title")
                rating = data.get("rating")
                
                if not all([artist, title, rating]):
                    return jsonify({"success": False, "error": "Données manquantes"}), 400
                
                # Créer ou mettre à jour la piste dans Supabase
                track_data = {
                    'artist': artist,
                    'title': title,
                    'deezer_id': data.get('deezer_id'),
                    'preview_url': data.get('preview_url'),
                    'album': data.get('album'),
                    'duration': data.get('duration'),
                    'cover_url': data.get('cover_url')
                }
                
                try:
                    # Ajouter la piste si elle n'existe pas
                    track_id = self.supabase_service.create_track(track_data)
                    
                    # Ajouter la notation
                    success = self.supabase_service.add_rating(
                        current_user.email, track_id, int(rating)
                    )
                    
                    if success:
                        # Récupérer les nouvelles statistiques
                        rating_info = self.supabase_service.get_track_stats(artist, title)
                        return jsonify({
                            "success": True,
                            "message": "Notation ajoutée avec succès",
                            "avg_rating": rating_info.get('average_rating', 0),
                            "count": rating_info.get('total_ratings', 0)
                        })
                    else:
                        return jsonify({"success": False, "error": "Erreur lors de l'ajout de la notation"}), 500
                        
                except Exception as e:
                    return jsonify({"success": False, "error": f"Erreur serveur: {str(e)}"}), 500
                    
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route("/register", methods=["GET", "POST"])
        def register():
            """Page d'inscription"""
            if request.method == "POST":
                email = request.form.get("email", "").strip()
                username = request.form.get("username", "").strip()
                password = request.form.get("password", "").strip()
                
                if not all([email, username, password]):
                    flash("Tous les champs sont requis", "error")
                    return render_template("register.html")
                
                success, message = self.auth_service.register_user(email, username, password)
                
                if success:
                    flash(message, "success")
                    return redirect(url_for("login"))
                else:
                    flash(message, "error")
            
            return render_template("register.html")
        
        @self.app.route("/login", methods=["GET", "POST"])
        def login():
            """Page de connexion"""
            if request.method == "POST":
                email = request.form.get("email", "").strip()
                password = request.form.get("password", "").strip()
                
                if not email or not password:
                    flash("Email et mot de passe requis", "error")
                    return render_template("login.html")
                
                success, message, user = self.auth_service.login_user(email, password)
                
                if success:
                    login_user(user, remember=True)
                    flash(message, "success")
                    return redirect(url_for("home"))
                else:
                    flash(message, "error")
            
            return render_template("login.html")
        
        @self.app.route("/logout")
        @login_required
        def logout():
            """Déconnexion"""
            logout_user()
            flash("Déconnexion réussie", "success")
            return redirect(url_for("home"))
        
        @self.app.route("/verify")
        def verify():
            """Vérification d'email"""
            email = request.args.get("email")
            token = request.args.get("token")
            
            if not email or not token:
                flash("Lien de vérification invalide", "error")
                return redirect(url_for("home"))
            
            success, message = self.auth_service.verify_user_email(email, token)
            
            if success:
                flash(message, "success")
                return redirect(url_for("login"))
            else:
                flash(message, "error")
                return redirect(url_for("home"))
        
        @self.app.route("/top-rated")
        def top_rated():
            """Page des morceaux les mieux notés"""
            tracks = self.supabase_service.get_top_rated_tracks(limit=20)
            return render_template("top_rated.html", tracks=tracks)
        
        @self.app.route("/my-ratings")
        @login_required
        def my_ratings():
            """Page des morceaux notés par l'utilisateur"""
            tracks = self.supabase_service.get_user_ratings(current_user.email)
            return render_template("my_ratings.html", tracks=tracks)
        
        @self.app.route("/stats")
        def stats():
            """API pour les statistiques"""
            return jsonify(self.supabase_service.get_global_stats())
        
        @self.app.route('/profile/config', methods=['GET', 'POST'])
        @login_required
        def profile_config():
            """Page de configuration du profil"""
            user_id = current_user.id if hasattr(current_user, 'id') else current_user.email
            user = self.supabase_service.get_user_profile(user_id)
            
            if not user:
                flash('Utilisateur non trouvé', 'error')
                return redirect(url_for('home'))
            
            messages = []
            
            if request.method == 'POST':
                try:
                    # Récupérer les données du formulaire
                    profile_data = {
                        'username': request.form.get('username'),
                        'full_name': request.form.get('full_name'),
                        'bio': request.form.get('bio'),
                        'favorite_genres': request.form.get('favorite_genres'),
                        'location': request.form.get('location')
                    }
                    
                    # Gestion de l'upload d'avatar
                    if 'avatar' in request.files:
                        file = request.files['avatar']
                        if file and file.filename and file.filename != '':
                            # Lire les données du fichier
                            file_data = file.read()
                            avatar_url = self.supabase_service.upload_avatar(user_id, file_data, file.filename)
                            if avatar_url:
                                profile_data['avatar_url'] = avatar_url
                                messages.append({'type': 'success', 'text': 'Photo de profil mise à jour avec succès!'})
                            else:
                                messages.append({'type': 'error', 'text': 'Erreur lors de l\'upload de la photo'})
                    
                    # Mettre à jour le profil
                    if self.supabase_service.update_user_profile(user_id, profile_data):
                        messages.append({'type': 'success', 'text': 'Profil mis à jour avec succès!'})
                        # Récupérer les données mises à jour
                        user = self.supabase_service.get_user_profile(user_id)
                    else:
                        messages.append({'type': 'error', 'text': 'Erreur lors de la mise à jour du profil'})
                        
                except Exception as e:
                    messages.append({'type': 'error', 'text': f'Erreur: {str(e)}'})
            
            # Récupérer les statistiques utilisateur
            user_stats = self.supabase_service.get_user_statistics(user_id)
            
            return render_template('profile_config.html', 
                             current_user=user, 
                             user_stats=user_stats, 
                             messages=messages)

    def run(self, **kwargs):
        """Lance l'application"""
        self.app.run(**kwargs)

# Point d'entrée de l'application
def create_app(config_name='default'):
    """Factory pour créer l'application"""
    return SoundJuryApp(config_name)

if __name__ == "__main__":
    # Créer et lancer l'application
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
