from flask import Flask

app = Flask(__name__)


@app.route("/home", methods=['GET'])
def index():
    return {"Name": ["Fahd", "Khalid", "Jhone"]}


if __name__ == "__main__":
    app.run(debug=True)