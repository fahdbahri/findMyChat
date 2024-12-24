from flask import Flask
from flask_cors import CORS
from youtube_services import PodcastSearchEngine

app = Flask(__name__)
CORS(app)

@app.route("/home", methods=['GET'])
def index():
    return {"Name": ["Fahd", "Khalid", "Jhone"]}


if __name__ == "__main__":
    app.run(debug=True)