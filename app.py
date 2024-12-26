import db
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route("/products.json")
def index():
    return db.products_all()

@app.route("/products/<id>.json", methods=["PATCH"])
def update(id):
    product = db.products_find_by_id(id)
    name = request.form.get("name") or product["name"]
    image_url = request.form.get("image_url") or product["image_url"]
    description = request.form.get("description") or product["description"]
    price = request.form.get("price") or product["price"]
    category = request.form.get("category") or product["category"]
    tax = request.form.get("tax") or product["tax"]
    total = request.form.get("total") or product["total"]
    return db.products_update_by_id(id, name, image_url, description, price, category, tax, total)

@app.route("/products.json", methods=["POST"])
def create():
    name = request.form.get("name")
    image_url = request.form.get("image_url")
    description = request.form.get("description")
    price = request.form.get("price")
    category = request.form.get("category")
    tax = request.form.get("tax")
    total = request.form.get("total")
    return db.products_create(name, image_url, description, price, category, tax, total)

@app.route("/products/<id>.json")
def show(id):
    return db.products_find_by_id(id)


@app.route("/products/<id>.json", methods=["DELETE"])
def destroy(id):
    return db.products_destroy_by_id(id)