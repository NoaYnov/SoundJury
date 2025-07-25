"""
SoundJury - Application principale
Architecture professionnelle avec classes et services
"""
import os
from datetime import timedelta
from dataclasses import replace
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env du dossier parent
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

# Configuration
from .core.config import config

# Modèles
from .models.user import User
from .models.track import Track
from .models.rating import RatingManager

# Services
from .services.auth_service import AuthService
from .services.deezer_service import DeezerMusicService
from .services.supabase_service import SupabaseService

class SoundJuryApp:
    """Application principale SoundJury"""
    
    def __init__(self, config_name='default'):
        self.app = Flask(__name__)
        self.config = config
        
        # Configuration de l'application Flask
        self.app.config.from_object(self.config)
        
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
        self.login_manager.session_protection = "strong"
        self.login_manager.remember_cookie_duration = None  # Session permanente
        
        # Configurer la session
        self.app.permanent_session_lifetime = timedelta(hours=24)
        
        # Configurer les routes
        self._setup_routes()
        self._setup_login_manager()
        self._setup_template_context()
    
    def _setup_template_context(self):
        """Configure le contexte global des templates"""
        @self.app.context_processor
        def inject_user():
            """Injecter current_user dans tous les templates"""
            return dict(current_user=current_user)
    
    def _setup_login_manager(self):
        """Configure Flask-Login"""
        @self.login_manager.user_loader
        def load_user(user_id):
            """Charger un utilisateur par son ID (Supabase UUID ou email)"""
            try:
                # Essayer de récupérer le profil par ID
                profile_data = self.supabase_service.get_user_profile(user_id)
                if profile_data:
                    return User(
                        id=profile_data.get('id'),
                        email=profile_data['email'],
                        username=profile_data.get('username', profile_data.get('full_name', profile_data['email'].split('@')[0])),
                        is_verified=profile_data.get('is_verified', True)
                    )
                
                # Si pas trouvé par ID, essayer par email (fallback)
                user_data = self.supabase_service.get_user(user_id)
                if user_data:
                    return User(
                        id=user_data.get('id'),
                        email=user_data['email'],
                        username=user_data.get('username', user_data.get('full_name', user_data['email'].split('@')[0])),
                        is_verified=user_data.get('is_verified', True)
                    )
                
                return None
            except Exception as e:
                print(f"Erreur lors du chargement de l'utilisateur {user_id}: {e}")
                return None
    
    def _setup_routes(self):
        """Configure toutes les routes de l'application"""
        
        @self.app.route("/")
        def home():
            """Page d'accueil avec morceaux tendance"""
            print(f"DEBUG HOME: current_user.is_authenticated = {current_user.is_authenticated}")
            if current_user.is_authenticated:
                print(f"DEBUG HOME: User connecté - ID: {current_user.get_id()}, Email: {current_user.email}")
            
            tracks = self.music_service.get_trending_tracks(limit=10)
            stats = self.supabase_service.get_global_stats()
            
            # Ajouter les informations de notation aux morceaux
            tracks_with_ratings = []
            for track in tracks:
                # Enrichir le track avec les données de notation
                rating_info = self.supabase_service.get_track_stats(track.artist, track.title)
                avg_rating = rating_info.get('average_rating', 0.0) if rating_info else 0.0
                rating_count = rating_info.get('total_ratings', 0) if rating_info else 0
                
                # Ajouter la note de l'utilisateur actuel si connecté
                user_rating = None
                if current_user.is_authenticated:
                    user_rating = self.supabase_service.get_user_rating(
                        current_user.email, track.artist, track.title
                    )
                    user_rating = user_rating if user_rating else 0
                
                # Créer une nouvelle instance avec toutes les informations
                track_with_rating = replace(
                    track,
                    avg_rating=avg_rating,
                    rating_count=rating_count,
                    user_rating=user_rating
                )
                
                tracks_with_ratings.append(track_with_rating)
            
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
                            # Créer une nouvelle instance avec les informations de notation
                            track_with_rating = replace(
                                track,
                                avg_rating=rating_info.get('average_rating', 0.0),
                                rating_count=rating_info.get('total_ratings', 0)
                            )
                            tracks.append(track_with_rating)
                        else:
                            # La track garde ses valeurs par défaut (0.0, 0)
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
        @self.app.route("/api/rate", methods=["POST"])
        @login_required
        def rate():
            """API pour noter un morceau"""
            try:
                print(f"DEBUG RATE: User connecté - ID: {current_user.get_id()}, Email: {current_user.email}")
                
                if not current_user.is_verified:
                    return jsonify({"success": False, "error": "Compte non vérifié"}), 403
                
                data = request.get_json()
                if not data:
                    return jsonify({"success": False, "error": "Aucune donnée JSON reçue"}), 400
                
                artist = data.get("artist")
                title = data.get("title")
                rating = data.get("rating")
                
                print(f"DEBUG RATE: Données reçues - Artist: {artist}, Title: {title}, Rating: {rating}")
                
                if not all([artist, title, rating]):
                    return jsonify({"success": False, "error": "Données manquantes (artist, title, rating requis)"}), 400
                
                # Valider la note
                try:
                    rating_value = int(rating)
                    if not 1 <= rating_value <= 5:
                        return jsonify({"success": False, "error": "La note doit être entre 1 et 5"}), 400
                except (ValueError, TypeError):
                    return jsonify({"success": False, "error": "Format de note invalide"}), 400
                
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
                
                print(f"DEBUG RATE: Création/recherche de la piste...")
                
                # Ajouter la piste si elle n'existe pas (avec user_id pour RLS)
                user_id = current_user.get_id()
                track_id = self.supabase_service.create_track(track_data, user_id)
                
                if not track_id:
                    return jsonify({"success": False, "error": "Impossible de créer ou trouver la piste"}), 500
                
                print(f"DEBUG RATE: Track ID trouvé: {track_id}")
                
                # Ajouter la notation avec l'ID utilisateur
                user_id = current_user.get_id()
                rating_result = self.supabase_service.add_rating_by_id(
                    user_id, track_id, rating_value
                )
                
                print(f"DEBUG RATE: Résultat notation: {rating_result}")
                
                if rating_result.get("success"):
                    # Récupérer les nouvelles statistiques
                    rating_info = self.supabase_service.get_track_stats(artist, title)
                    return jsonify({
                        "success": True,
                        "message": "Notation ajoutée avec succès",
                        "avg_rating": rating_info.get('average_rating', 0) if rating_info else 0,
                        "count": rating_info.get('total_ratings', 0) if rating_info else 0
                    })
                else:
                    error_msg = rating_result.get("error", "Erreur lors de l'ajout de la notation")
                    return jsonify({"success": False, "error": error_msg}), 500
                        
            except Exception as e:
                print(f"DEBUG RATE: Exception - {str(e)}")
                import traceback
                traceback.print_exc()
                return jsonify({"success": False, "error": f"Erreur serveur: {str(e)}"}), 500
        
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
                identifier = request.form.get("email", "").strip()  # On garde 'email' comme nom de champ pour la compatibilité
                password = request.form.get("password", "").strip()
                
                if not identifier or not password:
                    flash("Identifiant et mot de passe requis", "error")
                    return render_template("login.html")
                
                success, message, user = self.auth_service.login_user(identifier, password)
                
                if success and user:
                    print(f"DEBUG: Connexion réussie pour user ID: {user.get_id()}, email: {user.email}, username: {user.username}")
                    
                    # Marquer la session comme permanente
                    session.permanent = True
                    
                    login_result = login_user(user, remember=True)
                    print(f"DEBUG: login_user result: {login_result}")
                    print(f"DEBUG: current_user après login: {current_user}")
                    print(f"DEBUG: current_user.is_authenticated: {current_user.is_authenticated}")
                    
                    flash(message, "success")
                    return redirect(url_for("home"))
                else:
                    print(f"DEBUG: Échec de connexion - Success: {success}, Message: {message}, User: {user}")
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
            user_id = current_user.get_id()
            tracks = self.supabase_service.get_user_ratings(user_id)
            return render_template("my_ratings.html", tracks=tracks)
        
        @self.app.route("/stats")
        def stats():
            """API pour les statistiques"""
            return jsonify(self.supabase_service.get_global_stats())
        
        @self.app.route('/profile/config', methods=['GET', 'POST'])
        @login_required
        def profile_config():
            """Page de configuration du profil"""
            user_id = current_user.get_id()
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
                    
                    print(f"DEBUG: Données du formulaire reçues: {profile_data}")
                    
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
                    print(f"DEBUG: Tentative de mise à jour pour user_id: {user_id}")
                    update_success = self.supabase_service.update_user_profile(user_id, profile_data)
                    
                    if update_success:
                        messages.append({'type': 'success', 'text': 'Profil mis à jour avec succès!'})
                        # Récupérer les données mises à jour
                        user = self.supabase_service.get_user_profile(user_id)
                        print(f"DEBUG: Profil après mise à jour: {user}")
                    else:
                        messages.append({'type': 'error', 'text': 'Erreur lors de la mise à jour du profil - Vérifiez que les colonnes bio, location, favorite_genres existent dans la table profiles'})
                        
                except Exception as e:
                    messages.append({'type': 'error', 'text': f'Erreur: {str(e)}'})
            
            # Récupérer les statistiques utilisateur
            user_stats = self.supabase_service.get_user_statistics(user_id)
            
            return render_template('profile_config.html', 
                             user=user,
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
