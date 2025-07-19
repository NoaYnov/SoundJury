-- Configuration des tables pour SoundJury sur Supabase
-- Exécuter ces commandes dans l'éditeur SQL de Supabase

-- 1. Créer la table des utilisateurs (étend auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID REFERENCES auth.users ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE,
    full_name TEXT,
    avatar_url TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    PRIMARY KEY (id)
);

-- 2. Créer la table des morceaux
CREATE TABLE IF NOT EXISTS public.tracks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    album TEXT,
    duration TEXT,
    image_url TEXT,
    spotify_url TEXT,
    deezer_url TEXT,
    youtube_url TEXT,
    preview_url TEXT,
    external_id TEXT, -- ID depuis Spotify/Deezer
    genres TEXT[],
    release_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    UNIQUE(artist, title)
);

-- 3. Créer la table des notations
CREATE TABLE IF NOT EXISTS public.ratings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    track_id UUID REFERENCES public.tracks(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    UNIQUE(user_id, track_id)
);

-- 4. Créer la table des statistiques de morceaux (pour optimiser les requêtes)
CREATE TABLE IF NOT EXISTS public.track_stats (
    track_id UUID REFERENCES public.tracks(id) ON DELETE CASCADE PRIMARY KEY,
    total_ratings INTEGER DEFAULT 0,
    average_rating DECIMAL(3,2) DEFAULT 0.0,
    rating_1 INTEGER DEFAULT 0,
    rating_2 INTEGER DEFAULT 0,
    rating_3 INTEGER DEFAULT 0,
    rating_4 INTEGER DEFAULT 0,
    rating_5 INTEGER DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- 5. Créer des index pour optimiser les performances
CREATE INDEX IF NOT EXISTS idx_ratings_user_id ON public.ratings(user_id);
CREATE INDEX IF NOT EXISTS idx_ratings_track_id ON public.ratings(track_id);
CREATE INDEX IF NOT EXISTS idx_ratings_rating ON public.ratings(rating);
CREATE INDEX IF NOT EXISTS idx_tracks_artist ON public.tracks(artist);
CREATE INDEX IF NOT EXISTS idx_tracks_title ON public.tracks(title);
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_username ON public.profiles(username);

-- 6. Créer les politiques RLS (Row Level Security)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tracks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ratings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.track_stats ENABLE ROW LEVEL SECURITY;

-- Politiques pour les profils
CREATE POLICY "Les utilisateurs peuvent voir tous les profils" ON public.profiles
    FOR SELECT USING (true);

CREATE POLICY "Les utilisateurs peuvent mettre à jour leur propre profil" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Les utilisateurs peuvent créer leur propre profil" ON public.profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Politiques pour les morceaux
CREATE POLICY "Tout le monde peut voir les morceaux" ON public.tracks
    FOR SELECT USING (true);

CREATE POLICY "Les utilisateurs connectés peuvent créer des morceaux" ON public.tracks
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Politiques pour les notations
CREATE POLICY "Tout le monde peut voir les notations" ON public.ratings
    FOR SELECT USING (true);

CREATE POLICY "Les utilisateurs peuvent créer leurs propres notations" ON public.ratings
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Les utilisateurs peuvent mettre à jour leurs propres notations" ON public.ratings
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Les utilisateurs peuvent supprimer leurs propres notations" ON public.ratings
    FOR DELETE USING (auth.uid() = user_id);

-- Politiques pour les statistiques
CREATE POLICY "Tout le monde peut voir les statistiques" ON public.track_stats
    FOR SELECT USING (true);

CREATE POLICY "Seuls les utilisateurs connectés peuvent modifier les statistiques" ON public.track_stats
    FOR ALL USING (auth.role() = 'authenticated');

-- 7. Créer des fonctions pour mettre à jour automatiquement les statistiques
CREATE OR REPLACE FUNCTION update_track_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculer les nouvelles statistiques
    INSERT INTO public.track_stats (track_id, total_ratings, average_rating, rating_1, rating_2, rating_3, rating_4, rating_5)
    SELECT 
        COALESCE(NEW.track_id, OLD.track_id),
        COUNT(*),
        ROUND(AVG(rating::DECIMAL), 2),
        COUNT(*) FILTER (WHERE rating = 1),
        COUNT(*) FILTER (WHERE rating = 2),
        COUNT(*) FILTER (WHERE rating = 3),
        COUNT(*) FILTER (WHERE rating = 4),
        COUNT(*) FILTER (WHERE rating = 5)
    FROM public.ratings 
    WHERE track_id = COALESCE(NEW.track_id, OLD.track_id)
    ON CONFLICT (track_id) DO UPDATE SET
        total_ratings = EXCLUDED.total_ratings,
        average_rating = EXCLUDED.average_rating,
        rating_1 = EXCLUDED.rating_1,
        rating_2 = EXCLUDED.rating_2,
        rating_3 = EXCLUDED.rating_3,
        rating_4 = EXCLUDED.rating_4,
        rating_5 = EXCLUDED.rating_5,
        updated_at = NOW();
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- 8. Créer les triggers pour mettre à jour les statistiques
CREATE TRIGGER update_track_stats_trigger
    AFTER INSERT OR UPDATE OR DELETE ON public.ratings
    FOR EACH ROW EXECUTE FUNCTION update_track_stats();

-- 9. Créer une fonction pour créer automatiquement le profil utilisateur
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name, avatar_url)
    VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'avatar_url');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 10. Créer le trigger pour les nouveaux utilisateurs (supprimer d'abord s'il existe)
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 11. Créer des vues pour simplifier les requêtes
CREATE OR REPLACE VIEW public.tracks_with_stats AS
SELECT 
    t.*,
    COALESCE(ts.total_ratings, 0) as total_ratings,
    COALESCE(ts.average_rating, 0.0) as average_rating,
    COALESCE(ts.rating_1, 0) as rating_1,
    COALESCE(ts.rating_2, 0) as rating_2,
    COALESCE(ts.rating_3, 0) as rating_3,
    COALESCE(ts.rating_4, 0) as rating_4,
    COALESCE(ts.rating_5, 0) as rating_5
FROM public.tracks t
LEFT JOIN public.track_stats ts ON t.id = ts.track_id;

CREATE OR REPLACE VIEW public.user_ratings AS
SELECT 
    r.*,
    t.title,
    t.artist,
    t.album,
    t.image_url,
    p.username,
    p.full_name
FROM public.ratings r
JOIN public.tracks t ON r.track_id = t.id
JOIN public.profiles p ON r.user_id = p.id;

-- 12. Créer une fonction pour rechercher des morceaux
CREATE OR REPLACE FUNCTION public.search_tracks(search_query TEXT, limit_count INTEGER DEFAULT 20)
RETURNS TABLE(
    id UUID,
    title TEXT,
    artist TEXT,
    album TEXT,
    duration TEXT,
    image_url TEXT,
    spotify_url TEXT,
    deezer_url TEXT,
    youtube_url TEXT,
    preview_url TEXT,
    total_ratings INTEGER,
    average_rating DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.id,
        t.title,
        t.artist,
        t.album,
        t.duration,
        t.image_url,
        t.spotify_url,
        t.deezer_url,
        t.youtube_url,
        t.preview_url,
        COALESCE(ts.total_ratings, 0) as total_ratings,
        COALESCE(ts.average_rating, 0.0) as average_rating
    FROM public.tracks t
    LEFT JOIN public.track_stats ts ON t.id = ts.track_id
    WHERE 
        t.title ILIKE '%' || search_query || '%' 
        OR t.artist ILIKE '%' || search_query || '%'
        OR t.album ILIKE '%' || search_query || '%'
    ORDER BY 
        ts.average_rating DESC NULLS LAST,
        ts.total_ratings DESC NULLS LAST,
        t.title ASC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;
