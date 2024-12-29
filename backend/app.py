from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_services import PodcastSearchEngine



app = Flask(__name__)
CORS(app)

# Initialize the search engine once
search_engine = PodcastSearchEngine()

@app.route("/home", methods=['POST'])
def search_videos():
    try:


        usr_query = request.json["search-input"]  
        results = search_engine.search_podcast(usr_query)
        return jsonify(results)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)