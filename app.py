import db
from flask import Flask, request

app = Flask(__name__)

@app.route("/products.json")
def index():
    return db.products_all()

@app.route("/products.json", methods=["POST"])
def create():
    name = request.form.get("name")
    description = request.form.get("description")
    price = request.form.get("price")
    category = request.form.get("category")
    return db.products_create(name, description, price, category)

@app.route("/products/<id>.json")
def show(id):
    return db.products_find_by_id(id)
