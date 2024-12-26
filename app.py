import db
from flask import Flask, request

app = Flask(__name__)

@app.route("/products.json")
def index():
    return db.products_all()

@app.route("/products/<id>.json", methods=["PATCH"])
def update(id):
    product = db.products_find_by_id(id)
    name = request.form.get("name") or product["name"]
    description = request.form.get("description") or product["description"]
    price = request.form.get("price") or product["price"]
    category = request.form.get("category") or product["category"]
    return db.products_update_by_id(id, name, description, price, category)

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
