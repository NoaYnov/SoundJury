# Configuration des Emails pour SoundJury

## 🚀 Configuration Rapide avec Gmail (Recommandé)

### Étape 1: Activer l'authentification à 2 facteurs
1. Allez sur votre [compte Google](https://myaccount.google.com/)
2. Sécurité → Authentification à 2 facteurs → Activer

### Étape 2: Créer un mot de passe d'application
1. Retournez dans Sécurité → Authentification à 2 facteurs
2. Cliquez sur "Mots de passe des applications"
3. Sélectionnez "Autre" et tapez "SoundJury"
4. **Copiez le mot de passe généré** (16 caractères)

### Étape 3: Configuration dans .env
Créez un fichier `.env` dans le dossier `soundjury/` :
```
SECRET_KEY=your-super-secret-key-here-change-me
MAIL_USERNAME=votre-email@gmail.com
MAIL_PASSWORD=abcd-efgh-ijkl-mnop
MAIL_DEFAULT_SENDER=votre-email@gmail.com
```

**⚠️ Important** : Utilisez le mot de passe d'application, pas votre mot de passe Gmail normal !

## 📧 Autres Fournisseurs Email

### Outlook/Hotmail
```
MAIL_SERVER=smtp.live.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=votre-email@outlook.com
MAIL_PASSWORD=votre-mot-de-passe
```

### Yahoo Mail
```
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=votre-email@yahoo.com
MAIL_PASSWORD=votre-mot-de-passe-app
```

### SendGrid (Service professionnel)
```
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=votre-clé-api-sendgrid
```

## 🧪 Test de Configuration

Après configuration, testez avec ce script :

```python
# test_email.py
from email_service import email_service
from flask import Flask

app = Flask(__name__)
email_service.init_app(app)

with app.app_context():
    success = email_service.send_verification_email(
        "votre-email@test.com", 
        "http://localhost:5000/test", 
        "TestUser"
    )
    print("✅ Email envoyé !" if success else "❌ Erreur email")
```

## 🔒 Sécurité

- Ne jamais committer le fichier `.env`
- Utilisez des mots de passe d'application, pas vos vrais mots de passe
- Changez la `SECRET_KEY` en production
- Pour la production, utilisez des services comme SendGrid ou Mailgun

## 🚨 Mode Développement Sans Email

Si vous ne voulez pas configurer d'email immédiatement :

1. Les comptes peuvent être créés
2. Pour marquer un compte comme vérifié manuellement :

```python
# Dans le terminal Python
from auth import user_manager
user_manager.verify_user("email@example.com")
```

## 🎯 Vérification Fonctionnement

1. Créez un compte sur votre application
2. Vérifiez les logs pour voir si l'email est envoyé
3. Si configuré correctement, vous recevrez un email de vérification
4. Cliquez sur le lien pour activer le compte

Le système fonctionne même sans email configuré, mais la vérification sera manuelle.
