# 🎧 SoundJury - Guide de Démarrage Ultra-Rapide

## ✨ Système d'Authentification Intégré !

**Problème résolu** : Plus possible de noter en actualisant la page ! 
Un système complet avec comptes utilisateurs et vérification email a été ajouté.

## 🚀 Démarrage en 30 secondes

```bash
# 1. Installer les dépendances
pip install flask flask-login flask-mail werkzeug itsdangerous email-validator spotipy requests

# 2. Lancer l'application
cd soundjury
python app.py

# 3. Ouvrir dans le navigateur
# http://localhost:5000
```

## 🔐 Fonctionnalités d'Authentification

### ✅ **Protection Complète**
- **Inscription obligatoire** pour noter
- **Vérification email** automatique
- **Une seule note par utilisateur** par morceau
- **Sessions sécurisées** persistantes

### 📱 **Nouvelles Pages**
- `/register` - Créer un compte
- `/login` - Se connecter  
- `/logout` - Se déconnecter
- Navigation intégrée dans toutes les pages

### 🛡️ **Sécurité**
- Mots de passe hachés (Werkzeug)
- Tokens temporaires pour vérification
- Protection contre les votes multiples
- Validation des données côté client/serveur

## 📧 Configuration Email (Optionnelle)

Pour que les emails de vérification fonctionnent :

1. **Créez un fichier `.env`** :
```
SECRET_KEY=votre-clé-secrète-ici
MAIL_USERNAME=votre-email@gmail.com  
MAIL_PASSWORD=votre-mot-de-passe-app-gmail
MAIL_DEFAULT_SENDER=votre-email@gmail.com
```

2. **Configurez Gmail** (voir `EMAIL_SETUP.md` pour les détails)

**⚠️ Sans email configuré** : Les comptes peuvent être créés, mais la vérification est manuelle.

## 🎯 Test Rapide

1. **Ouvrez** http://localhost:5000
2. **Cliquez** "S'inscrire" 
3. **Créez un compte** (email@test.com / motdepasse)
4. **Recherchez une musique**
5. **Notez** avec les étoiles
6. **Essayez de noter à nouveau** → Impossible ! ✅

## 📊 Données Stockées

- `users.json` - Comptes utilisateurs (emails hachés)
- `ratings.json` - Notes par utilisateur (impossible de dupliquer)

## 🎉 C'est Prêt !

Le système est **100% fonctionnel** et empêche totalement les abus de notation.
Chaque utilisateur ne peut voter qu'une seule fois par morceau.

**Prochaine étape recommandée** : Migrer vers Supabase (gratuit) pour un vrai déploiement.
