from flask import Flask, jsonify, request
from database import db
from models.snack import Snack

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:admin123@127.0.0.1:3306/daily_diet"

db.init_app(app)

@app.route("/", methods=["GET"])
def index():
    return "<h1>Daily Diet API</h1>"

if __name__ == '__main__':
    app.run(debug=True)