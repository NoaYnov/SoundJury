"""
Service d'authentification avec Supabase
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from models.user import User
from config import Config
from services.supabase_service import SupabaseService

class AuthService:
    """Service d'authentification avec gestion des utilisateurs via Supabase"""
    
    def __init__(self, config: Config):
        self.config = config
        self.supabase_service = SupabaseService()
    
    def register_user(self, email: str, username: str, password: str) -> tuple[bool, str]:
        """Enregistre un nouvel utilisateur"""
        try:
            # Vérifier si l'utilisateur existe déjà
            existing_user = self.supabase_service.get_user(email)
            if existing_user:
                return False, "Un compte existe déjà avec cette adresse email"
            
            # Créer l'utilisateur dans Supabase
            user_data = {
                'email': email,
                'username': username,
                'password': password,
                'is_verified': False
            }
            
            user_id = self.supabase_service.create_user(user_data)
            if user_id:
                return True, "Compte créé avec succès ! Vous pouvez maintenant vous connecter."
            else:
                return False, "Erreur lors de la création du compte"
                
        except Exception as e:
            return False, f"Erreur lors de l'enregistrement: {str(e)}"
    
    def login_user(self, email: str, password: str) -> tuple[bool, str, Optional[User]]:
        """Connecte un utilisateur"""
        try:
            user_data = self.supabase_service.authenticate_user(email, password)
            if user_data:
                # Créer un objet User à partir des données Supabase
                user = User(
                    email=user_data['email'],
                    username=user_data['username'],
                    password_hash='',  # Pas de hash local avec Supabase Auth
                    is_verified=user_data.get('is_verified', True)
                )
                return True, "Connexion réussie", user
            else:
                return False, "Email ou mot de passe incorrect", None
                
        except Exception as e:
            return False, f"Erreur lors de la connexion: {str(e)}", None
    
    def verify_user_email(self, email: str, token: str) -> tuple[bool, str]:
        """Vérifie l'email d'un utilisateur"""
        # Cette fonctionnalité pourrait être implémentée avec Supabase Auth
        return True, "Email vérifié avec succès"
    
    def get_user(self, email: str) -> Optional[User]:
        """Récupère un utilisateur par email"""
        try:
            user_data = self.supabase_service.get_user(email)
            if user_data:
                return User(
                    email=user_data['email'],
                    username=user_data['username'],
                    password_hash='',  # Pas de hash local avec Supabase Auth
                    is_verified=user_data.get('is_verified', True)
                )
            return None
        except Exception:
            return None
    
    def get_user_stats(self) -> dict:
        """Retourne les statistiques des utilisateurs"""
        return self.supabase_service.get_user_stats()
    
    def _send_verification_email(self, user: User) -> bool:
        """Envoie l'email de vérification"""
        try:
            # Configuration du serveur SMTP
            server = smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT)
            server.starttls()
            server.login(self.config.SMTP_USERNAME, self.config.SMTP_PASSWORD)
            
            # Création du message
            msg = MIMEMultipart()
            msg['From'] = self.config.SMTP_USERNAME
            msg['To'] = user.email
            msg['Subject'] = "🎵 Vérification de votre compte SoundJury"
            
            # Corps du message
            verification_link = f"http://localhost:5000/verify?email={user.email}&token={user.verification_token}"
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #00ffcc, #0066cc); padding: 2rem; text-align: center; color: white;">
                    <h1>🎧 Bienvenue sur SoundJury !</h1>
                    <p>Salut {user.username} ! Votre compte a été créé avec succès.</p>
                </div>
                
                <div style="padding: 2rem; background: #f9f9f9;">
                    <h2>Vérification de votre compte</h2>
                    <p>Pour activer votre compte et commencer à noter vos morceaux préférés, cliquez sur le lien ci-dessous :</p>
                    
                    <div style="text-align: center; margin: 2rem 0;">
                        <a href="{verification_link}" 
                           style="background: #00ffcc; color: white; padding: 1rem 2rem; text-decoration: none; border-radius: 8px; font-weight: bold;">
                            ✅ Vérifier mon compte
                        </a>
                    </div>
                    
                    <p>Si le bouton ne fonctionne pas, copiez ce lien dans votre navigateur :</p>
                    <p style="word-break: break-all; background: #eee; padding: 1rem; border-radius: 4px;">
                        {verification_link}
                    </p>
                </div>
                
                <div style="padding: 1rem; text-align: center; color: #666; font-size: 0.9rem;">
                    <p>🎵 L'équipe SoundJury<br>
                    Votre avis musical compte vraiment !</p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Envoi du message
            server.send_message(msg)
            server.quit()
            
            print(f"Email de vérification envoyé à {user.email}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")
            return False
