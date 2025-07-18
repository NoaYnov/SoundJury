#!/usr/bin/env python3
"""
Script de nettoyage des ratings pour éliminer les doublons
et garder seulement les données globales des titres
"""

import json
import os

def clean_ratings():
    """Nettoie le fichier ratings.json pour éliminer les doublons"""
    ratings_file = "soundjury/ratings.json"
    
    if not os.path.exists(ratings_file):
        print("Fichier ratings.json non trouvé")
        return
    
    # Charger les données actuelles
    with open(ratings_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Données avant nettoyage: {len(data)} entrées")
    
    # Séparer les votes individuels des statistiques globales
    user_votes = {}  # clé_utilisateur -> données_vote
    track_stats = {}  # track_id -> statistiques_globales
    
    for key, value in data.items():
        if "_at_" in key and "_dot_" in key:
            # C'est un vote individuel
            user_votes[key] = value
        else:
            # C'est une statistique globale de titre
            track_stats[key] = value
    
    print(f"Votes individuels trouvés: {len(user_votes)}")
    print(f"Statistiques globales trouvées: {len(track_stats)}")
    
    # Reconstruire les statistiques globales à partir des votes individuels
    rebuilt_stats = {}
    
    for vote_key, vote_data in user_votes.items():
        track_id = vote_data.get('track_id')
        if not track_id:
            continue
            
        if track_id not in rebuilt_stats:
            rebuilt_stats[track_id] = {
                'total': 0,
                'count': 0,
                'artist': vote_data.get('artist'),
                'title': vote_data.get('title'),
                'voters': []
            }
        
        # Ajouter ce vote
        rebuilt_stats[track_id]['total'] += vote_data.get('rating', 0)
        rebuilt_stats[track_id]['count'] += 1
        rebuilt_stats[track_id]['voters'].append(vote_data.get('user_email'))
    
    # Calculer les moyennes
    for track_id, stats in rebuilt_stats.items():
        if stats['count'] > 0:
            stats['average'] = round(stats['total'] / stats['count'], 1)
        else:
            stats['average'] = 0
    
    # Créer le nouveau fichier de données
    new_data = {}
    
    # Ajouter les votes individuels
    new_data.update(user_votes)
    
    # Ajouter les statistiques globales reconstruites
    new_data.update(rebuilt_stats)
    
    print(f"Données après nettoyage: {len(new_data)} entrées")
    print(f"Titres uniques: {len(rebuilt_stats)}")
    
    # Sauvegarder
    with open(ratings_file, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
    
    print("Nettoyage terminé!")
    
    # Afficher un résumé
    print("\nRésumé des titres:")
    for track_id, stats in rebuilt_stats.items():
        print(f"- {stats['artist']} - {stats['title']}: {stats['average']}/5 ({stats['count']} votes)")

if __name__ == "__main__":
    clean_ratings()
