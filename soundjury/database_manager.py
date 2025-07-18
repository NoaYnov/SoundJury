# Module pour gérer différents types de bases de données
import json
import os
from abc import ABC, abstractmethod
from database_config import get_database_config

class DatabaseInterface(ABC):
    @abstractmethod
    def save_rating(self, track_id, rating_data):
        pass
    
    @abstractmethod
    def get_rating(self, track_id):
        pass
    
    @abstractmethod
    def get_all_ratings(self):
        pass

class JSONDatabase(DatabaseInterface):
    def __init__(self, filename="ratings.json"):
        self.filename = filename
    
    def _load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_data(self, data):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except IOError:
            return False
    
    def save_rating(self, track_id, rating_data):
        data = self._load_data()
        data[track_id] = rating_data
        return self._save_data(data)
    
    def get_rating(self, track_id):
        data = self._load_data()
        return data.get(track_id, {
            "total": 0,
            "count": 0,
            "average": 0
        })
    
    def get_all_ratings(self):
        return self._load_data()

class SupabaseDatabase(DatabaseInterface):
    def __init__(self, url, key):
        try:
            from supabase import create_client
            self.client = create_client(url, key)
        except ImportError:
            raise ImportError("supabase-py package required. Install with: pip install supabase")
    
    def save_rating(self, track_id, rating_data):
        try:
            # Vérifier si l'entrée existe
            result = self.client.table('ratings').select('*').eq('track_id', track_id).execute()
            
            if result.data:
                # Mettre à jour
                self.client.table('ratings').update(rating_data).eq('track_id', track_id).execute()
            else:
                # Insérer
                rating_data['track_id'] = track_id
                self.client.table('ratings').insert(rating_data).execute()
            return True
        except Exception as e:
            print(f"Erreur Supabase: {e}")
            return False
    
    def get_rating(self, track_id):
        try:
            result = self.client.table('ratings').select('*').eq('track_id', track_id).execute()
            if result.data:
                return result.data[0]
            return {"total": 0, "count": 0, "average": 0}
        except Exception as e:
            print(f"Erreur Supabase: {e}")
            return {"total": 0, "count": 0, "average": 0}
    
    def get_all_ratings(self):
        try:
            result = self.client.table('ratings').select('*').execute()
            return {item['track_id']: item for item in result.data}
        except Exception as e:
            print(f"Erreur Supabase: {e}")
            return {}

# Factory pour créer la bonne instance de base de données
def get_database():
    db_type = get_database_config()
    
    if db_type == 'supabase':
        from database_config import SUPABASE_URL, SUPABASE_KEY
        return SupabaseDatabase(SUPABASE_URL, SUPABASE_KEY)
    elif db_type == 'json':
        return JSONDatabase()
    else:
        # Par défaut, utiliser JSON
        return JSONDatabase()
