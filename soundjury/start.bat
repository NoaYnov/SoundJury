@echo off
echo 🎧 Demarrage de SoundJury...
echo.

echo 📦 Installation des dependances...
pip install -r requirements.txt

echo.
echo 🚀 Lancement de l'application...
echo ✅ L'application sera disponible sur http://localhost:5000
echo ⚠️  Les emails de verification seront affiches dans la console
echo.

python app.py

pause
