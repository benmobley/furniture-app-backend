import db
from flask import Flask, request,jsonify, session
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Products
@app.route("/products.json")
def products_index():
    return db.products_all()

@app.route("/products/<int:id>.json", methods=["GET"])
def products_show(id):
    return db.products_find_by_id(id)

@app.route("/products/<int:id>.json", methods=["PATCH"])
def products_update(id):
    product = db.products_find_by_id(id)
    name = request.form.get("name", product["name"])
    image_url = request.form.get("image_url", product["image_url"])
    description = request.form.get("description", product["description"])
    price = request.form.get("price", product["price"])
    category = request.form.get("category", product["category"])
    tax = request.form.get("tax", product["tax"])
    total = request.form.get("total", product["total"])
    return db.products_update_by_id(id, name, image_url, description, price, category, tax, total)

@app.route('/products.json', methods=['POST'])
def create_product():
    name = request.form.get("name")
    price = request.form.get("price")
    description = request.form.get("description")
    quantity = request.form.get("quantity")
    categories = request.form.getlist("categories")  
    image_urls = request.form.getlist("image_urls") 
    db.products_create(name, price, description, quantity, categories, image_urls)
    return jsonify({"message": "Product successfully created"}), 201

@app.route("/products/<int:id>.json", methods=["DELETE"])
def products_destroy(id):
    return db.products_destroy_by_id(id)

app.secret_key = "supersecretkey"

# Create a new user
@app.route("/users", methods=["POST"])
def users_create():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")  
    hashed_password = db.hash_password(password)  
    db.users_create(name, email, hashed_password)
    return jsonify({"message": "User successfully created"}), 201


@app.route("/sessions", methods=["POST"])
def sessions_create():
    email = request.form.get("email")
    password = request.form.get("password")  
    user = db.users_find_by_email(email)

    if user and db.check_password(password, user["password_digest"]):  
        session["user_id"] = user["id"]  
        return jsonify({"message": "Logged in successfully", "user": {"id": user["id"], "name": user["name"], "email": user["email"]}})
    return jsonify({"error": "Invalid email or password"}), 401

@app.route("/sessions", methods=["DELETE"])
def sessions_destroy():
    session.pop("user_id", None) 
    return jsonify({"message": "Logged out successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True)