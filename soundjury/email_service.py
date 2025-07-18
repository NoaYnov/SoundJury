# Service d'envoi d'emails pour SoundJury
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_mail import Mail, Message

class EmailService:
    def __init__(self, app=None):
        self.mail = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialise le service email avec Flask"""
        # Configuration Gmail par défaut (gratuit)
        app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
        app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', '587'))
        app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
        app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
        app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
        app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
        app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])
        
        self.mail = Mail(app)
    
    def send_verification_email(self, email, verification_url, username=None):
        """Envoie un email de vérification"""
        # Si l'email n'est pas configuré, afficher le lien dans la console
        if not self.mail or not os.getenv('MAIL_USERNAME'):
            print(f"\n{'='*60}")
            print(f"📧 EMAIL DE VÉRIFICATION (mode développement)")
            print(f"{'='*60}")
            print(f"Pour: {email}")
            print(f"Nom: {username or 'Utilisateur'}")
            print(f"Lien de vérification: {verification_url}")
            print(f"{'='*60}")
            print(f"⚠️  Copiez ce lien dans votre navigateur pour vérifier le compte")
            print(f"{'='*60}\n")
            return True
        
        try:
            subject = "🎧 Vérifiez votre compte SoundJury"
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
                    .header {{ background: linear-gradient(135deg, #00ffcc, #0066cc); padding: 30px; text-align: center; }}
                    .header h1 {{ color: white; margin: 0; font-size: 28px; }}
                    .content {{ padding: 30px; }}
                    .button {{ display: inline-block; background: #00ffcc; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0; }}
                    .footer {{ background: #f8f8f8; padding: 20px; text-align: center; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎧 SoundJury</h1>
                        <p style="color: white; margin: 10px 0 0 0; opacity: 0.9;">Votre plateforme de notation musicale</p>
                    </div>
                    <div class="content">
                        <h2>Bienvenue{f" {username}" if username else ""} !</h2>
                        <p>Merci de vous être inscrit sur SoundJury. Pour commencer à noter vos morceaux préférés, veuillez vérifier votre adresse email en cliquant sur le bouton ci-dessous :</p>
                        
                        <div style="text-align: center;">
                            <a href="{verification_url}" class="button">✅ Vérifier mon email</a>
                        </div>
                        
                        <p><strong>Ce lien expire dans 1 heure</strong> pour votre sécurité.</p>
                        
                        <p>Si vous n'avez pas créé ce compte, vous pouvez ignorer cet email.</p>
                        
                        <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                        
                        <h3>🎵 Que pouvez-vous faire sur SoundJury ?</h3>
                        <ul>
                            <li>Rechercher et découvrir de nouveaux morceaux</li>
                            <li>Noter vos chansons préférées de 1 à 5 étoiles</li>
                            <li>Voir le classement des morceaux les mieux notés</li>
                            <li>Partager vos goûts musicaux avec la communauté</li>
                        </ul>
                    </div>
                    <div class="footer">
                        <p>🎧 SoundJury - Votre avis compte !</p>
                        <p>Si le bouton ne fonctionne pas, copiez ce lien : <br>{verification_url}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_body = f"""
            Bienvenue sur SoundJury !
            
            Merci de vous être inscrit. Pour vérifier votre compte, cliquez sur ce lien :
            {verification_url}
            
            Ce lien expire dans 1 heure.
            
            Si vous n'avez pas créé ce compte, ignorez cet email.
            
            L'équipe SoundJury
            """
            
            msg = Message(
                subject=subject,
                recipients=[email],
                body=text_body,
                html=html_body
            )
            
            self.mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Erreur envoi email: {e}")
            return False
    
    def send_password_reset_email(self, email, reset_url, username=None):
        """Envoie un email de réinitialisation de mot de passe"""
        if not self.mail:
            print("⚠️  Service email non configuré")
            return False
        
        try:
            subject = "🔒 Réinitialisation de votre mot de passe SoundJury"
            
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
                    .header {{ background: linear-gradient(135deg, #ff6b35, #f7931e); padding: 30px; text-align: center; }}
                    .header h1 {{ color: white; margin: 0; font-size: 28px; }}
                    .content {{ padding: 30px; }}
                    .button {{ display: inline-block; background: #ff6b35; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0; }}
                    .footer {{ background: #f8f8f8; padding: 20px; text-align: center; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎧 SoundJury</h1>
                        <p style="color: white; margin: 10px 0 0 0; opacity: 0.9;">Réinitialisation de mot de passe</p>
                    </div>
                    <div class="content">
                        <h2>Réinitialisation demandée</h2>
                        <p>Vous avez demandé une réinitialisation de votre mot de passe. Cliquez sur le bouton ci-dessous pour définir un nouveau mot de passe :</p>
                        
                        <div style="text-align: center;">
                            <a href="{reset_url}" class="button">🔒 Nouveau mot de passe</a>
                        </div>
                        
                        <p><strong>Ce lien expire dans 30 minutes</strong> pour votre sécurité.</p>
                        
                        <p>Si vous n'avez pas demandé cette réinitialisation, ignorez cet email. Votre mot de passe restera inchangé.</p>
                    </div>
                    <div class="footer">
                        <p>🎧 SoundJury - Sécurité avant tout !</p>
                        <p>Si le bouton ne fonctionne pas, copiez ce lien : <br>{reset_url}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg = Message(
                subject=subject,
                recipients=[email],
                html=html_body
            )
            
            self.mail.send(msg)
            return True
            
        except Exception as e:
            print(f"Erreur envoi email: {e}")
            return False

# Instance globale
email_service = EmailService()
