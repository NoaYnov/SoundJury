from flask import Flask, render_template, request, jsonify
from music_api import get_fast_tracks, get_full_track_data

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    query = ""
    tracks = []
    if request.method == "POST":
        query = request.form.get("query")
        if query:
            tracks = get_fast_tracks(query)
    return render_template("index.html", query=query, tracks=tracks)

@app.route("/details", methods=["POST"])
def details():
    try:
        data = request.get_json()
        print("Requête AJAX reçue :", data)
        artist = data.get("artist")
        title = data.get("title")
        artist_id = data.get("artist_id")

        result = get_full_track_data(artist, title, artist_id)
        return jsonify(result)
    except Exception as e:
        print("Erreur /details :", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
