"""
Service Supabase pour SoundJury
Gestion de la base de données et de l'authentification
"""

import os
from typing import List, Dict, Optional, Any
from supabase import create_client, Client
from datetime import datetime
import uuid
from dotenv import load_dotenv
import hashlib

# Charger les variables d'environnement depuis le fichier .env du dossier parent
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)

class SupabaseService:
    """Service pour interagir avec Supabase"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL et SUPABASE_KEY doivent être configurés")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
    
    # === GESTION DES UTILISATEURS ===
    
    def create_user_auth(self, email: str, password: str, full_name: str = None) -> Dict:
        """Créer un nouvel utilisateur avec Supabase Auth"""
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "email_redirect_to": None,  # Désactive la redirection d'email
                    "data": {
                        "full_name": full_name
                    }
                }
            })
            
            # Si l'utilisateur est créé, marquer l'email comme confirmé dans la table profiles
            if response.user:
                try:
                    # Créer ou mettre à jour le profil avec email confirmé
                    self.client.table("profiles").upsert({
                        "id": response.user.id,
                        "email": email,
                        "full_name": full_name,
                        "username": full_name or email.split('@')[0],  # Username par défaut
                        "is_verified": True,  # Marquer comme vérifié par défaut
                        "created_at": "now()",
                        "updated_at": "now()"
                    }).execute()
                except Exception as profile_error:
                    print(f"Erreur lors de la création du profil: {profile_error}")
            
            return {"success": True, "user": response.user, "session": response.session}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def login_user(self, email: str, password: str) -> Dict:
        """Connecter un utilisateur"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return {"success": True, "user": response.user, "session": response.session}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def logout_user(self) -> Dict:
        """Déconnecter l'utilisateur"""
        try:
            self.client.auth.sign_out()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Récupérer le profil utilisateur"""
        try:
            response = self.client.table("profiles").select("*").eq("id", user_id).single().execute()
            
            if response.data:
                profile = response.data
                
                # S'assurer que le username est défini selon les règles demandées
                if not profile.get('username'):
                    # Si pas de username, utiliser full_name ou une partie de l'email
                    username = profile.get('full_name') or profile.get('email', '').split('@')[0]
                    
                    # Mettre à jour le profil
                    try:
                        self.client.table("profiles").update({
                            "username": username
                        }).eq("id", user_id).execute()
                        profile['username'] = username
                    except Exception as update_error:
                        print(f"Erreur lors de la mise à jour du username: {update_error}")
                        profile['username'] = username  # Au moins pour cette session
                
                return profile
            
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération du profil: {e}")
            return None
    
    def update_user_profile(self, user_id: str, profile_data: Dict) -> bool:
        """Mettre à jour le profil utilisateur"""
        try:
            # Filtrer les données autorisées
            allowed_fields = ['username', 'full_name', 'avatar_url', 'bio', 'favorite_genres', 'location']
            filtered_data = {k: v for k, v in profile_data.items() if k in allowed_fields and v is not None}
            
            if not filtered_data:
                return True
            
            filtered_data['updated_at'] = datetime.utcnow().isoformat()
            
            response = self.client.table("profiles").update(filtered_data).eq("id", user_id).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Erreur lors de la mise à jour du profil: {e}")
            return False
    
    def upload_avatar(self, user_id: str, file_data: bytes, file_name: str) -> Optional[str]:
        """Upload d'un avatar utilisateur"""
        try:
            # Créer un nom de fichier unique
            file_extension = file_name.split('.')[-1] if '.' in file_name else 'jpg'
            unique_filename = f"avatars/{user_id}.{file_extension}"
            
            # Upload vers Supabase Storage
            response = self.client.storage.from_("avatars").upload(unique_filename, file_data, {"upsert": "true"})
            
            if response:
                # Récupérer l'URL publique
                avatar_url = self.client.storage.from_("avatars").get_public_url(unique_filename)
                
                # Mettre à jour le profil avec la nouvelle URL
                self.update_user_profile(user_id, {"avatar_url": avatar_url})
                
                return avatar_url
            
            return None
        except Exception as e:
            print(f"Erreur lors de l'upload de l'avatar: {e}")
            return None
    
    def get_user_statistics(self, user_id: str) -> Dict:
        """Récupérer les statistiques d'un utilisateur"""
        try:
            # Compter le nombre de ratings
            ratings_response = self.client.table("ratings").select("rating").eq("user_id", user_id).execute()
            
            if ratings_response.data:
                ratings = [r['rating'] for r in ratings_response.data]
                total_ratings = len(ratings)
                avg_rating = sum(ratings) / total_ratings if total_ratings > 0 else 0
                tracks_rated = total_ratings  # Chaque rating = un morceau noté
            else:
                total_ratings = 0
                avg_rating = 0
                tracks_rated = 0
            
            return {
                "total_ratings": total_ratings,
                "avg_rating": round(avg_rating, 1),
                "tracks_rated": tracks_rated
            }
        except Exception as e:
            print(f"Erreur lors de la récupération des statistiques: {e}")
            return {"total_ratings": 0, "avg_rating": 0, "tracks_rated": 0}

    # === MÉTHODES ADDITIONNELLES POUR L'INTÉGRATION ===
    
    def get_user(self, email: str) -> Optional[Dict]:
        """Récupérer un utilisateur par email"""
        try:
            response = self.client.table("profiles").select("*").eq("email", email).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération de l'utilisateur: {e}")
            return None
    
    def create_user(self, user_data: Dict) -> Optional[str]:
        """Créer un utilisateur avec les données fournies"""
        try:
            # Utiliser Supabase Auth pour créer l'utilisateur
            auth_response = self.client.auth.sign_up({
                "email": user_data['email'],
                "password": user_data['password'],
                "options": {
                    "data": {
                        "username": user_data['username'],
                        "full_name": user_data.get('full_name', user_data['username'])
                    }
                }
            })
            
            if auth_response.user:
                # Le profil sera créé automatiquement par le trigger
                # on_auth_user_created, mais on peut mettre à jour avec des infos supplémentaires
                try:
                    # Attendre un moment pour que le trigger se déclenche
                    import time
                    time.sleep(0.5)
                    
                    # Mettre à jour le profil avec le username
                    profile_update = {
                        "username": user_data['username'],
                        "is_verified": user_data.get('is_verified', False)
                    }
                    
                    self.client.table("profiles").update(profile_update).eq("id", auth_response.user.id).execute()
                except Exception as profile_error:
                    print(f"Avertissement - Erreur lors de la mise à jour du profil: {profile_error}")
                    # Ce n'est pas critique, l'utilisateur est créé
                
                return auth_response.user.id
            
            return None
        except Exception as e:
            print(f"Erreur lors de la création de l'utilisateur: {e}")
            return None
    
    def authenticate_user(self, identifier: str, password: str) -> Optional[Dict]:
        """Authentifier un utilisateur avec email ou username"""
        try:
            # Déterminer si l'identifiant est un email ou un username
            is_email = '@' in identifier
            
            if is_email:
                # Authentification directe avec email
                auth_response = self.client.auth.sign_in_with_password({
                    "email": identifier,
                    "password": password
                })
            else:
                # Chercher l'email associé au username
                profile_response = self.client.table("profiles").select("email").eq("username", identifier).execute()
                if not profile_response.data:
                    return None
                
                email = profile_response.data[0]['email']
                # Authentification avec l'email trouvé
                auth_response = self.client.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
            
            if auth_response.user:
                # Récupérer le profil utilisateur complet
                profile_response = self.client.table("profiles").select("*").eq("id", auth_response.user.id).execute()
                if profile_response.data:
                    profile_data = profile_response.data[0]
                    
                    # S'assurer que le username est défini correctement
                    if not profile_data.get('username'):
                        # Si pas de username, utiliser full_name ou une partie de l'email
                        username = profile_data.get('full_name') or profile_data.get('email', '').split('@')[0]
                        # Mettre à jour le profil
                        self.client.table("profiles").update({
                            "username": username
                        }).eq("id", auth_response.user.id).execute()
                        profile_data['username'] = username
                    
                    return profile_data
            
            return None
        except Exception as e:
            error_msg = str(e)
            print(f"Erreur lors de l'authentification: {error_msg}")
            
            # Si l'erreur est liée à l'email non confirmé, essayer de confirmer automatiquement
            if "Email not confirmed" in error_msg:
                try:
                    # Forcer la connexion en marquant l'email comme confirmé
                    # Note: Cette approche nécessite des privilèges admin sur Supabase
                    print("Tentative de connexion forcée...")
                    return None  # Pour l'instant on retourne None, mais on pourrait implémenter une logique spéciale
                except Exception:
                    pass
            
            return None
    
    def create_track(self, track_data: Dict, user_id: str = None) -> Optional[str]:
        """Créer une piste si elle n'existe pas - Version compatible avec le schéma actuel"""
        try:
            # Vérifier si la piste existe déjà
            response = self.client.table("tracks").select("id").eq("artist", track_data['artist']).eq("title", track_data['title']).execute()
            
            if response.data:
                print(f"DEBUG CREATE_TRACK: Piste existante trouvée - ID: {response.data[0]['id']}")
                return response.data[0]['id']
            
            # Créer la nouvelle piste avec seulement les colonnes qui existent
            new_track = {
                "title": track_data['title'],
                "artist": track_data['artist']
            }
            
            # Ajouter les colonnes optionnelles qui existent réellement dans votre schéma
            optional_fields = [
                ("album", track_data.get('album')),
                ("duration", track_data.get('duration')),  
                ("deezer_id", track_data.get('deezer_id')),
                ("preview_url", track_data.get('preview_url')),
                ("image_url", track_data.get('cover_url') or track_data.get('image_url'))
            ]
            
            for field_name, field_value in optional_fields:
                if field_value is not None and field_value != "":
                    new_track[field_name] = field_value
            
            print(f"DEBUG CREATE_TRACK: Tentative d'insertion avec: {new_track}")
            
            # Insertion directe sans created_by
            response = self.client.table("tracks").insert(new_track).execute()
            if response.data:
                track_id = response.data[0].get('id')
                print(f"DEBUG CREATE_TRACK: Succès - Track ID: {track_id}")
                return track_id
            else:
                print(f"DEBUG CREATE_TRACK: Aucune donnée retournée")
                return None
                
        except Exception as e:
            print(f"DEBUG CREATE_TRACK: Erreur lors de l'insertion: {e}")
            
            # Si l'erreur mentionne une colonne inexistante, essayer avec le minimum
            if 'does not exist' in str(e) or 'column' in str(e).lower():
                print("DEBUG CREATE_TRACK: Tentative avec colonnes minimales seulement...")
                try:
                    minimal_track = {
                        "title": track_data['title'],
                        "artist": track_data['artist']
                    }
                    
                    response = self.client.table("tracks").insert(minimal_track).execute()
                    if response.data:
                        track_id = response.data[0].get('id')
                        print(f"DEBUG CREATE_TRACK: Succès minimal - Track ID: {track_id}")
                        return track_id
                except Exception as e2:
                    print(f"DEBUG CREATE_TRACK: Échec même avec colonnes minimales: {e2}")
            
            # Instructions pour résoudre le problème RLS
            if 'row-level security' in str(e).lower():
                print("DEBUG CREATE_TRACK: Erreur RLS - Consultez GUIDE_SUPABASE_RLS.md")
                print("SOLUTION RAPIDE: ALTER TABLE tracks DISABLE ROW LEVEL SECURITY;")
            
            return None
    
    def get_user_stats(self) -> Dict:
        """Récupérer les statistiques des utilisateurs"""
        try:
            response = self.client.table("profiles").select("*").execute()
            total_users = len(response.data) if response.data else 0
            
            # Compter les utilisateurs vérifiés
            verified_users = len([u for u in response.data if u.get('is_verified', False)]) if response.data else 0
            
            return {
                "total_users": total_users,
                "verified_users": verified_users,
                "pending_verification": total_users - verified_users
            }
        except Exception as e:
            print(f"Erreur lors de la récupération des stats utilisateurs: {e}")
            return {"total_users": 0, "verified_users": 0, "pending_verification": 0}
    
    def get_track_stats(self, artist: str, title: str) -> Optional[Dict]:
        """Récupérer les statistiques d'une piste par artiste et titre"""
        try:
            # Récupérer la piste
            track_response = self.client.table("tracks").select("id").eq("artist", artist).eq("title", title).execute()
            
            if not track_response.data:
                return None
            
            track_id = track_response.data[0]['id']
            
            # Récupérer les statistiques
            stats_response = self.client.table("track_stats").select("*").eq("track_id", track_id).execute()
            
            if stats_response.data:
                return stats_response.data[0]
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération des stats de piste: {e}")
            return None
    
    def get_user_rating(self, user_email: str, artist: str, title: str) -> Optional[int]:
        """Récupérer la note d'un utilisateur pour une piste"""
        try:
            # Récupérer l'utilisateur
            user = self.get_user(user_email)
            if not user:
                return None
            
            # Récupérer la piste
            track_response = self.client.table("tracks").select("id").eq("artist", artist).eq("title", title).execute()
            if not track_response.data:
                return None
            
            track_id = track_response.data[0]['id']
            
            # Récupérer la notation
            rating_response = self.client.table("ratings").select("rating").eq("user_id", user['id']).eq("track_id", track_id).execute()
            
            if rating_response.data:
                return rating_response.data[0]['rating']
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération de la note utilisateur: {e}")
            return None
    
    def get_top_rated_tracks(self, limit: int = 20) -> List[Dict]:
        """Récupérer les pistes les mieux notées"""
        try:
            # Essayer d'abord la fonction RPC si elle existe
            try:
                response = self.client.rpc('get_top_rated_tracks_v2', {
                    'limit_count': limit
                }).execute()
                
                if response.data:
                    return response.data
            except Exception as e:
                print(f"RPC fonction non disponible: {e}")
            
            # Fallback : requête directe avec join
            tracks_response = self.client.table("tracks").select("*, ratings(rating)").execute()
            
            tracks = []
            track_stats = {}
            
            # Calculer les statistiques pour chaque track
            for track in tracks_response.data or []:
                track_id = track['id']
                ratings = track.get('ratings', [])
                
                if ratings:
                    rating_values = [r['rating'] for r in ratings if r['rating'] is not None]
                    if rating_values:
                        avg_rating = sum(rating_values) / len(rating_values)
                        track_stats[track_id] = {
                            'track': track,
                            'avg_rating': avg_rating,
                            'rating_count': len(rating_values)
                        }
            
            # Trier par note moyenne et nombre de votes
            sorted_tracks = sorted(
                track_stats.values(),
                key=lambda x: (x['avg_rating'], x['rating_count']),
                reverse=True
            )
            
            # Formater le résultat
            for stat in sorted_tracks[:limit]:
                track = stat['track']
                track['avg_rating'] = round(stat['avg_rating'], 1)
                track['rating_count'] = stat['rating_count']
                # Compatibilité avec le template
                track['average'] = track['avg_rating']
                track['count'] = track['rating_count']
                tracks.append(track)
            
            return tracks
            
        except Exception as e:
            print(f"Erreur lors de la récupération des top pistes: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    # === GESTION DES MORCEAUX ===
    
    def get_or_create_track(self, title: str, artist: str, **kwargs) -> Dict:
        """Récupérer ou créer un morceau"""
        try:
            # Vérifier si le morceau existe déjà
            existing = self.client.table("tracks").select("*").eq("title", title).eq("artist", artist).execute()
            
            if existing.data:
                return {"success": True, "track": existing.data[0], "created": False}
            
            # Créer le morceau
            track_data = {
                "title": title,
                "artist": artist,
                "album": kwargs.get("album", ""),
                "duration": kwargs.get("duration", ""),
                "image_url": kwargs.get("image_url", ""),
                "spotify_url": kwargs.get("spotify_url", ""),
                "deezer_url": kwargs.get("deezer_url", ""),
                "youtube_url": kwargs.get("youtube_url", ""),
                "preview_url": kwargs.get("preview_url", ""),
                "external_id": kwargs.get("external_id", ""),
                "genres": kwargs.get("genres", []),
                "release_date": kwargs.get("release_date")
            }
            
            response = self.client.table("tracks").insert(track_data).execute()
            return {"success": True, "track": response.data[0], "created": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_tracks(self, query: str, limit: int = 20) -> List[Dict]:
        """Rechercher des morceaux"""
        try:
            response = self.client.rpc("search_tracks", {
                "search_query": query,
                "limit_count": limit
            }).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Erreur lors de la recherche: {e}")
            return []
    
    def get_trending_tracks(self, limit: int = 10) -> List[Dict]:
        """Récupérer les morceaux tendance"""
        try:
            response = self.client.from_("tracks_with_stats").select("*").order("average_rating", desc=True).order("total_ratings", desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Erreur lors de la récupération des tendances: {e}")
            return []
    
    # === GESTION DES NOTATIONS ===
    
    def add_rating(self, user_email: str, track_id: str, rating: int, comment: str = None) -> bool:
        """Ajouter ou mettre à jour une notation (version adaptée pour l'application)"""
        try:
            if not (1 <= rating <= 5):
                return False
            
            # Récupérer l'utilisateur
            user = self.get_user(user_email)
            if not user:
                return False
            
            rating_data = {
                "user_id": user['id'],
                "track_id": track_id,
                "rating": rating,
                "comment": comment,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Utiliser upsert pour créer ou mettre à jour
            response = self.client.table("ratings").upsert(rating_data).execute()
            return bool(response.data)
            
        except Exception as e:
            print(f"Erreur lors de l'ajout de la notation: {e}")
            return False
    
    def add_rating_by_id(self, user_id: str, track_id: str, rating: int, comment: str = None) -> Dict:
        """Ajouter ou mettre à jour une notation (version originale)"""
        try:
            print(f"DEBUG ADD_RATING: user_id={user_id}, track_id={track_id}, rating={rating}")
            
            if not (1 <= rating <= 5):
                return {"success": False, "error": "La note doit être entre 1 et 5"}
            
            # Vérifier si une notation existe déjà
            existing_rating = self.get_user_rating_by_id(user_id, track_id)
            
            rating_data = {
                "user_id": user_id,
                "track_id": track_id,
                "rating": rating,
                "comment": comment,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            print(f"DEBUG ADD_RATING: rating_data={rating_data}")
            print(f"DEBUG ADD_RATING: existing_rating={existing_rating}")
            
            if existing_rating:
                # Mettre à jour la notation existante
                response = self.client.table("ratings").update(rating_data).eq("user_id", user_id).eq("track_id", track_id).execute()
                print(f"DEBUG ADD_RATING: update response={response}")
            else:
                # Créer une nouvelle notation
                rating_data["created_at"] = datetime.utcnow().isoformat()
                response = self.client.table("ratings").insert(rating_data).execute()
                print(f"DEBUG ADD_RATING: insert response={response}")
            
            return {"success": True, "data": response.data}
            
        except Exception as e:
            print(f"DEBUG ADD_RATING: Exception={str(e)}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def get_user_rating_by_id(self, user_id: str, track_id: str) -> Optional[Dict]:
        """Récupérer la notation d'un utilisateur pour un morceau par ID"""
        try:
            response = self.client.table("ratings").select("*").eq("user_id", user_id).eq("track_id", track_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Erreur lors de la récupération de la notation: {e}")
            return None
    
    def get_track_ratings(self, track_id: str) -> List[Dict]:
        """Récupérer toutes les notations d'un morceau"""
        try:
            response = self.client.from_("user_ratings").select("*").eq("track_id", track_id).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Erreur lors de la récupération des notations: {e}")
            return []
    
    def get_user_ratings(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Récupérer toutes les notations d'un utilisateur avec les informations des tracks"""
        try:
            # Récupérer les ratings avec les informations des tracks
            response = self.client.table("ratings").select(
                "*, tracks(*)"
            ).eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
            
            if not response.data:
                return []
            
            # Reformater les données pour le template
            tracks_with_ratings = []
            for rating in response.data:
                if rating.get('tracks'):
                    track = rating['tracks']
                    track_id = track['id']
                    
                    # Ajouter la note de l'utilisateur à l'objet track
                    track['user_rating'] = rating['rating']
                    track['rating_date'] = rating['created_at']
                    track['comment'] = rating.get('comment', '')
                    track['timestamp'] = rating['created_at']
                    
                    # Calculer les statistiques globales pour ce track
                    try:
                        global_ratings_response = self.client.table("ratings").select("rating").eq("track_id", track_id).execute()
                        
                        if global_ratings_response.data:
                            global_ratings = [r['rating'] for r in global_ratings_response.data if r['rating'] is not None]
                            if global_ratings:
                                track['global_average'] = sum(global_ratings) / len(global_ratings)
                                track['global_count'] = len(global_ratings)
                            else:
                                track['global_average'] = 0
                                track['global_count'] = 0
                        else:
                            track['global_average'] = 0
                            track['global_count'] = 0
                    except Exception as e:
                        print(f"Erreur calcul stats globales pour track {track_id}: {e}")
                        track['global_average'] = 0
                        track['global_count'] = 0
                    
                    tracks_with_ratings.append(track)
            
            return tracks_with_ratings
        except Exception as e:
            print(f"Erreur lors de la récupération des notations utilisateur: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    # === STATISTIQUES ===
    
    def get_track_stats_by_id(self, track_id: str) -> Optional[Dict]:
        """Récupérer les statistiques d'un morceau par ID"""
        try:
            response = self.client.table("track_stats").select("*").eq("track_id", track_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Erreur lors de la récupération des statistiques: {e}")
            return None
    
    def get_global_stats(self) -> Dict:
        """Récupérer les statistiques globales"""
        try:
            # Compter le nombre total d'utilisateurs
            users_count = self.client.table("profiles").select("*", count="exact").execute().count
            
            # Compter le nombre total de morceaux
            tracks_count = self.client.table("tracks").select("*", count="exact").execute().count
            
            # Compter le nombre total de notations
            ratings_count = self.client.table("ratings").select("*", count="exact").execute().count
            
            # Calculer la note moyenne globale
            avg_response = self.client.table("ratings").select("rating").execute()
            if avg_response.data:
                ratings = [r["rating"] for r in avg_response.data]
                avg_rating = sum(ratings) / len(ratings) if ratings else 0
            else:
                avg_rating = 0
            
            return {
                "users_count": users_count,
                "tracks_count": tracks_count,
                "ratings_count": ratings_count,
                "average_rating": round(avg_rating, 2)
            }
        except Exception as e:
            print(f"Erreur lors de la récupération des statistiques globales: {e}")
            return {
                "users_count": 0,
                "tracks_count": 0,
                "ratings_count": 0,
                "average_rating": 0.0
            }
    
    # === UTILITAIRES ===
    
    def health_check(self) -> Dict:
        """Vérifier la santé de la connexion Supabase"""
        try:
            response = self.client.table("profiles").select("id").limit(1).execute()
            return {"success": True, "status": "healthy"}
        except Exception as e:
            return {"success": False, "error": str(e)}
