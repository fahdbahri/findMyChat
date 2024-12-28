from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_services import PodcastSearchEngine
import sqlite3



app = Flask(__name__)
CORS(app)

# Initialize the search engine once
search_engine = PodcastSearchEngine()

@app.route("/home", methods=['POST'])
def search_videos():
    try:


        print("Request received!")  # Debug line 1
        print("Request JSON:", request.json)  # Debug line 2
        usr_query = request.json["search-input"]

        # Debug the databasae 
        sqliteconnect = sqlite3.connect('podcast.db')
        cursor = sqliteconnect.cursor()
        print("connected to the SQLite")

        sqlite_query = """SELECT video_id FROM podcasts"""
        cursor.execute(sqlite_query)
        records = cursor.fetchall()
        print(len(records))
        print(records)

        

        results = search_engine.search_podcast(usr_query)
        return jsonify(results)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)