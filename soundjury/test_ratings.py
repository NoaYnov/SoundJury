#!/usr/bin/env python3
"""
Script de test pour vérifier le système de notation
"""

from ratings import add_rating, get_rating, get_top_rated_tracks

def test_rating_system():
    print("🧪 Test du système de notation...")
    
    # Test 1: Ajouter quelques notes
    print("\n1. Ajout de notes de test...")
    test_songs = [
        ("The Weeknd", "Blinding Lights", 5),
        ("The Weeknd", "Blinding Lights", 4),
        ("Billie Eilish", "Bad Guy", 4),
        ("Billie Eilish", "Bad Guy", 5),
        ("Billie Eilish", "Bad Guy", 3),
        ("Dua Lipa", "Levitating", 5),
    ]
    
    for artist, title, rating in test_songs:
        success = add_rating(artist, title, rating)
        print(f"   ✅ {artist} - {title}: {rating}/5 {'✓' if success else '✗'}")
    
    # Test 2: Vérifier les ratings
    print("\n2. Vérification des ratings...")
    for artist, title in [("The Weeknd", "Blinding Lights"), ("Billie Eilish", "Bad Guy")]:
        rating_info = get_rating(artist, title)
        print(f"   📊 {artist} - {title}: {rating_info['average']}/5 ({rating_info['count']} votes)")
    
    # Test 3: Top des morceaux
    print("\n3. Top des morceaux notés:")
    top_tracks = get_top_rated_tracks(5)
    for i, track in enumerate(top_tracks, 1):
        print(f"   🏆 #{i}: {track['artist']} - {track['title']} ({track['average']}/5)")
    
    print("\n✅ Tests terminés ! Le système fonctionne.")

if __name__ == "__main__":
    test_rating_system()
