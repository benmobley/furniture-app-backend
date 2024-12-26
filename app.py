import db
from flask import Flask, request

app = Flask(__name__)

@app.route("/products.json")
def index():
    return db.products_all()
