# Système de notation avec authentification utilisateur
from threading import Lock
from datetime import datetime
from database_manager import get_database

# Lock pour éviter les problèmes de concurrence
ratings_lock = Lock()

# Instance de base de données
db = get_database()

def get_track_id(artist, title):
    """Génère un ID unique pour une chanson basé sur l'artiste et le titre"""
    return f"{artist}_{title}".lower().replace(" ", "_")

def get_user_rating_key(track_id, user_email):
    """Génère une clé unique pour un vote utilisateur"""
    return f"{track_id}_{user_email}".replace("@", "_at_").replace(".", "_dot_")

def add_rating(artist, title, rating, user_email):
    """Ajoute ou modifie une note pour une chanson (1-5 étoiles) par un utilisateur spécifique"""
    if not (1 <= rating <= 5):
        return False, "Note invalide (1-5)"
    
    if not user_email:
        return False, "Utilisateur non connecté"
    
    track_id = get_track_id(artist, title)
    user_rating_key = get_user_rating_key(track_id, user_email)
    
    with ratings_lock:
        # Vérifier si l'utilisateur a déjà voté
        existing_user_rating = db.get_rating(user_rating_key)
        is_update = existing_user_rating.get("count", 0) > 0
        old_rating = existing_user_rating.get("rating", 0) if is_update else 0
        
        # Enregistrer/modifier le vote de l'utilisateur
        user_vote_data = {
            "rating": rating,
            "user_email": user_email,
            "track_id": track_id,
            "artist": artist,
            "title": title,
            "timestamp": datetime.now().isoformat(),
            "count": 1,  # Pour la compatibilité avec l'interface
            "total": rating,
            "average": rating
        }
        
        if not db.save_rating(user_rating_key, user_vote_data):
            return False, "Erreur de sauvegarde du vote"
        
        # Mettre à jour les statistiques globales du morceau
        current_rating = db.get_rating(track_id)
        
        if is_update:
            # Modification d'une note existante
            if current_rating.get("count", 0) > 0:
                current_rating["total"] = current_rating["total"] - old_rating + rating
                # Le count reste le même car c'est une modification
            else:
                # Cas où les stats globales auraient été perdues
                current_rating = {
                    "total": rating,
                    "count": 1,
                    "artist": artist,
                    "title": title,
                    "voters": [user_email]
                }
        else:
            # Nouvelle note
            if current_rating.get("count", 0) > 0:
                current_rating["total"] += rating
                current_rating["count"] += 1
                if "voters" not in current_rating:
                    current_rating["voters"] = []
                current_rating["voters"].append(user_email)
            else:
                current_rating = {
                    "total": rating,
                    "count": 1,
                    "artist": artist,
                    "title": title,
                    "voters": [user_email]
                }
        
        # Calculer la nouvelle moyenne
        current_rating["average"] = round(current_rating["total"] / current_rating["count"], 1)
        
        # Sauvegarder les stats globales
        success = db.save_rating(track_id, current_rating)
        
        if success:
            message = "Note modifiée avec succès !" if is_update else "Note ajoutée avec succès !"
            return True, message
        else:
            return False, "Erreur de mise à jour des statistiques"

def get_rating(artist, title):
    """Récupère les informations de notation pour une chanson"""
    track_id = get_track_id(artist, title)
    return db.get_rating(track_id)

def has_user_rated(artist, title, user_email):
    """Vérifie si un utilisateur a déjà noté un morceau"""
    if not user_email:
        return False
    
    track_id = get_track_id(artist, title)
    user_rating_key = get_user_rating_key(track_id, user_email)
    user_rating = db.get_rating(user_rating_key)
    
    return user_rating.get("count", 0) > 0

def get_user_rating(artist, title, user_email):
    """Récupère la note donnée par un utilisateur spécifique"""
    if not user_email:
        return None
    
    track_id = get_track_id(artist, title)
    user_rating_key = get_user_rating_key(track_id, user_email)
    user_rating = db.get_rating(user_rating_key)
    
    if user_rating.get("count", 0) > 0:
        return user_rating.get("rating")
    return None

def get_all_ratings():
    """Récupère tous les ratings"""
    return db.get_all_ratings()

def get_top_rated_tracks(limit=10):
    """Récupère les morceaux les mieux notés"""
    ratings_data = db.get_all_ratings()
    
    # Filtrer les morceaux avec au moins 1 vote et trier par moyenne
    rated_tracks = [
        {**data, "track_id": track_id} 
        for track_id, data in ratings_data.items() 
        if data.get("count", 0) > 0 and not "_at_" in track_id  # Exclure les votes individuels
    ]
    
    # Trier par moyenne décroissante, puis par nombre de votes
    rated_tracks.sort(key=lambda x: (x.get("average", 0), x.get("count", 0)), reverse=True)
    
    return rated_tracks[:limit]

def get_user_rated_tracks(user_email):
    """Récupère tous les titres notés par un utilisateur spécifique"""
    if not user_email:
        return []
    
    ratings_data = db.get_all_ratings()
    user_tracks = []
    
    # Rechercher tous les votes de cet utilisateur
    email_key = user_email.replace("@", "_at_").replace(".", "_dot_")
    
    for key, data in ratings_data.items():
        if f"_{email_key}" in key and data.get("user_email") == user_email:
            # Récupérer les stats globales du titre
            track_id = data.get("track_id")
            if track_id:
                global_stats = db.get_rating(track_id)
                user_tracks.append({
                    "track_id": track_id,
                    "artist": data.get("artist"),
                    "title": data.get("title"),
                    "user_rating": data.get("rating"),
                    "timestamp": data.get("timestamp"),
                    "global_average": global_stats.get("average", 0),
                    "global_count": global_stats.get("count", 0)
                })
    
    # Trier par timestamp décroissant (plus récent en premier)
    user_tracks.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return user_tracks
