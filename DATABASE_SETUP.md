# Configuration des Bases de Données Gratuites pour SoundJury

Ce guide vous explique comment configurer différentes bases de données gratuites pour stocker les notes des musiques.

## Option 1: Stockage JSON Local (Par défaut)
✅ **Avantages**: Aucune configuration, fonctionne immédiatement
❌ **Inconvénients**: Données locales uniquement, pas de partage entre utilisateurs

**Configuration**: Aucune, c'est le mode par défaut.

## Option 2: Supabase (PostgreSQL gratuit)
✅ **Avantages**: 500MB gratuit, interface web, APIs automatiques
✅ **Limites**: 500MB, 2 projets max

**Configuration**:
1. Créez un compte sur [supabase.com](https://supabase.com)
2. Créez un nouveau projet
3. Dans `SQL Editor`, exécutez cette requête pour créer la table :
```sql
CREATE TABLE ratings (
  id SERIAL PRIMARY KEY,
  track_id VARCHAR(255) UNIQUE NOT NULL,
  total INTEGER NOT NULL DEFAULT 0,
  count INTEGER NOT NULL DEFAULT 0,
  average DECIMAL(3,1) NOT NULL DEFAULT 0,
  artist VARCHAR(255),
  title VARCHAR(255),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```
4. Récupérez votre URL et clé API dans `Settings > API`
5. Créez un fichier `.env` dans le dossier `soundjury/` :
```
SUPABASE_URL=https://votre-projet.supabase.co
SUPABASE_KEY=votre-clé-anon
```
6. Installez la dépendance :
```bash
pip install supabase
```
7. Dans `database_config.py`, changez `USE_JSON_STORAGE = False`

## Option 3: MongoDB Atlas (NoSQL gratuit)
✅ **Avantages**: 512MB gratuit, très populaire
✅ **Limites**: 512MB, 3 clusters max

**Configuration**:
1. Créez un compte sur [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Créez un cluster gratuit (M0)
3. Configurez l'accès réseau (0.0.0.0/0 pour tous)
4. Créez un utilisateur de base de données
5. Récupérez la chaîne de connexion
6. Créez un fichier `.env` :
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/soundjury
```
7. Installez la dépendance :
```bash
pip install pymongo
```

## Option 4: PlanetScale (MySQL gratuit)
✅ **Avantages**: MySQL compatible, branches de base de données
✅ **Limites**: 1GB gratuit, 1 base de données

**Configuration**:
1. Créez un compte sur [planetscale.com](https://planetscale.com)
2. Créez une base de données
3. Créez une branche `main`
4. Récupérez la chaîne de connexion
5. Créez un fichier `.env` :
```
PLANETSCALE_DATABASE_URL=mysql://username:password@host/database?sslmode=require
```
6. Installez la dépendance :
```bash
pip install mysql-connector-python
```

## Option 5: Firebase Firestore (NoSQL Google)
✅ **Avantages**: Intégration Google, temps réel
✅ **Limites**: 1GB gratuit

**Configuration**:
1. Créez un projet sur [console.firebase.google.com](https://console.firebase.google.com)
2. Activez Firestore
3. Créez un compte de service et téléchargez le JSON
4. Créez un fichier `.env` :
```
FIREBASE_CREDENTIALS=path/to/serviceAccount.json
```
5. Installez la dépendance :
```bash
pip install firebase-admin
```

## Recommandation

Pour débuter rapidement: **Supabase** 
- Interface utilisateur claire
- Documentation excellente
- PostgreSQL (SQL standard)
- 500MB largement suffisant pour commencer

## Installation des dépendances

Créez un fichier `requirements.txt` avec les dépendances optionnelles :

```txt
flask
spotipy
requests
supabase>=1.0.0  # Pour Supabase
pymongo>=4.0.0   # Pour MongoDB
mysql-connector-python>=8.0.0  # Pour PlanetScale
firebase-admin>=6.0.0  # Pour Firebase
python-dotenv>=0.19.0  # Pour charger les variables .env
```

Puis installez :
```bash
pip install -r requirements.txt
```

## Sécurité

⚠️ **Important**: 
- Ne jamais committer le fichier `.env` dans Git
- Ajoutez `.env` dans votre `.gitignore`
- Utilisez des clés API avec des permissions minimales
