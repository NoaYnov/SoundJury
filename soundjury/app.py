from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from music_api import get_fast_tracks, get_full_track_data, get_trending_tracks
from ratings import add_rating, get_rating, get_top_rated_tracks, has_user_rated, get_user_rating, get_user_rated_tracks
from auth import user_manager, EmailVerification
from email_service import email_service
import os
import secrets

app = Flask(__name__)

# Configuration de sécurité
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(16))

# Configuration Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Vous devez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'

# Configuration email
email_service.init_app(app)

# Initialisation du vérificateur d'email
email_verifier = EmailVerification(app.config['SECRET_KEY'])

@login_manager.user_loader
def load_user(user_email):
    return user_manager.get_user(user_email)

@app.route("/")
def home():
    top_tracks = get_trending_tracks(limit=5)  # à implémenter dans music_api.py
    return render_template("home.html", tracks=top_tracks)

@app.route("/search", methods=["GET", "POST"])
def search():
    query = ""
    tracks = []
    if request.method == "POST":
        query = request.form.get("query")
        if query:
            tracks = get_fast_tracks(query)
    return render_template("index.html", query=query, tracks=tracks)

@app.route("/details", methods=["POST"])
def details():
    try:
        data = request.get_json()
        artist = data.get("artist")
        title = data.get("title")
        artist_id = data.get("artist_id")

        result = get_full_track_data(artist, title, artist_id)
        
        # Ajouter les informations de rating
        rating_info = get_rating(artist, title)
        result.update(rating_info)
        
        # Ajouter si l'utilisateur a déjà voté
        if current_user.is_authenticated:
            result['user_has_rated'] = has_user_rated(artist, title, current_user.email)
            result['user_rating'] = get_user_rating(artist, title, current_user.email)
        else:
            result['user_has_rated'] = False
            result['user_rating'] = None
        
        return jsonify(result)

    except Exception as e:
        print("Erreur backend /details :", e)  # très important pour debug
        return jsonify({"error": "internal error", "message": str(e)}), 500

@app.route("/rate", methods=["POST"])
@login_required
def rate_track():
    try:
        if not current_user.is_verified:
            return jsonify({"error": "Vous devez vérifier votre email pour noter des morceaux"}), 403
        
        data = request.get_json()
        artist = data.get("artist")
        title = data.get("title")
        rating = data.get("rating")
        
        if not artist or not title or rating is None:
            return jsonify({"error": "Données manquantes"}), 400
        
        success, error_msg = add_rating(artist, title, int(rating), current_user.email)
        if success:
            rating_info = get_rating(artist, title)
            return jsonify({
                "success": True,
                "average": rating_info["average"],
                "count": rating_info["count"],
                "message": error_msg  # error_msg contient maintenant le message de succès
            })
        else:
            return jsonify({"error": error_msg}), 400
            
    except Exception as e:
        print("Erreur backend /rate :", e)
        return jsonify({"error": "internal error", "message": str(e)}), 500

# Routes d'authentification
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        username = request.form.get("username", "").strip()
        
        # Validation basique
        if not email or not password:
            flash("Email et mot de passe requis", "error")
            return render_template("register.html")
        
        if len(password) < 6:
            flash("Le mot de passe doit faire au moins 6 caractères", "error")
            return render_template("register.html")
        
        # Créer l'utilisateur
        user, error = user_manager.create_user(email, password, username)
        
        if error:
            flash(error, "error")
            return render_template("register.html")
        
        # Générer le token de vérification
        token = email_verifier.generate_token(email)
        verification_url = url_for('verify_email', token=token, _external=True)
        
        # Envoyer l'email de vérification
        if email_service.send_verification_email(email, verification_url, username):
            flash("Compte créé ! Vérifiez votre email pour l'activer.", "success")
        else:
            flash("Compte créé, mais l'email de vérification n'a pas pu être envoyé. Contactez l'administrateur.", "warning")
        
        return redirect(url_for('login'))
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        
        user = user_manager.get_user(email)
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            flash(f"Bienvenue {user.username} !", "success")
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash("Email ou mot de passe incorrect", "error")
    
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Vous avez été déconnecté", "info")
    return redirect(url_for('home'))

@app.route("/verify-email/<token>")
def verify_email(token):
    email = email_verifier.verify_token(token)
    
    if email:
        if user_manager.verify_user(email):
            flash("Email vérifié avec succès ! Vous pouvez maintenant noter des morceaux.", "success")
            return redirect(url_for('login'))
        else:
            flash("Erreur lors de la vérification", "error")
    else:
        flash("Lien de vérification invalide ou expiré", "error")
    
    return redirect(url_for('register'))

@app.route("/top-rated")
def top_rated():
    """Page affichant les morceaux les mieux notés"""
    top_tracks = get_top_rated_tracks(limit=20)
    return render_template("top_rated.html", tracks=top_tracks)

@app.route("/stats")
def stats():
    """API pour obtenir les statistiques des ratings"""
    top_tracks = get_top_rated_tracks(limit=10)
    total_ratings = sum(track.get("count", 0) for track in top_tracks)
    
    return jsonify({
        "total_ratings": total_ratings,
        "total_tracks": len(top_tracks),
        "top_tracks": top_tracks[:5]  # Top 5 pour l'API
    })

@app.route("/my-ratings")
@login_required
def my_ratings():
    """Page affichant les titres notés par l'utilisateur connecté"""
    user_tracks = get_user_rated_tracks(current_user.email)
    return render_template("my_ratings.html", tracks=user_tracks)


if __name__ == "__main__":
    app.run(debug=True)