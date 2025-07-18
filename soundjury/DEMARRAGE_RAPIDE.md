# 🎧 SoundJury - Guide de Démarrage Rapide

## Lancement immédiat (Windows)

Double-cliquez sur `start.bat` ou ouvrez PowerShell et tapez :
```bash
.\start.bat
```

## Lancement manuel

1. **Installer les dépendances :**
   ```bash
   pip install -r requirements.txt
   ```

2. **Lancer l'application :**
   ```bash
   python app.py
   ```

3. **Ouvrir dans le navigateur :**
   ```
   http://localhost:5000
   ```

## 📧 Configuration Email (Optionnel)

Pour activer l'envoi d'emails réels, éditez le fichier `.env` :

```env
# Décommentez et configurez ces lignes :
MAIL_USERNAME=votre-email@gmail.com
MAIL_PASSWORD=votre-mot-de-passe-app-gmail
MAIL_DEFAULT_SENDER=votre-email@gmail.com
```

**Note :** En mode développement, les liens de vérification s'affichent dans la console.

## 🔥 Fonctionnalités

- ✅ **Recherche musicale** via l'API Spotify
- ✅ **Système de notation** (1-5 étoiles)
- ✅ **Authentification sécurisée** avec vérification email
- ✅ **Protection contre l'abus** (une note par utilisateur par chanson)
- ✅ **Top des morceaux** les mieux notés
- ✅ **Interface responsive** avec thème sombre/clair

## 🎵 Utilisation

1. **Créer un compte** avec votre email
2. **Vérifier votre email** (lien dans la console)
3. **Rechercher des morceaux** sur la page principale
4. **Noter vos favoris** de 1 à 5 étoiles
5. **Découvrir le top** des morceaux populaires

## 🛠 Développement

- **Base de données :** JSON (local) ou Supabase/MongoDB (production)
- **API musicale :** Spotify Web API
- **Framework :** Flask + Bootstrap
- **Authentification :** Flask-Login + email verification

Consultez `EMAIL_SETUP.md` pour la configuration Gmail complète.
