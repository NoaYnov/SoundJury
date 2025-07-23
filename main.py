#!/usr/bin/env python3
"""
SoundJury - Point d'entrée principal
Application de notation musicale collaborative
"""

import os
import sys

# Ajouter le dossier soundjury au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'soundjury'))

from soundjury.app import SoundJuryApp

def main():
    """Point d'entrée principal de l'application"""
    app = SoundJuryApp()
    
    # Configuration pour le développement
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    
    print(f"🎵 Démarrage de SoundJury sur {host}:{port}")
    print(f"🔧 Mode debug: {debug}")
    
    app.run(debug=debug, host=host, port=port)

if __name__ == "__main__":
    main()
