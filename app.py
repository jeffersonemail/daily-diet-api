from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "<h1>Daily Diet API</h1>"

if __name__ == '__main__':
    app.run(debug=True)