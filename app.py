import db_helpers as db  # Renamed db_helpers for consistency with coworker’s code
from flask import Flask, request, jsonify, g, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask.cli import with_appcontext
import click

# Initialize Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True)  # Allow cross-origin requests with credentials for session handling

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "supersecretkey"  # Session secret key

# Initialize extensions
db_instance = SQLAlchemy(app)  # SQLAlchemy for ORM
bcrypt = Bcrypt(app)  # Bcrypt for hashing passwords


# User model setup (SQLAlchemy)
class User(db_instance.Model):
    id = db_instance.Column(db_instance.Integer, primary_key=True)
    name = db_instance.Column(db_instance.String(50), nullable=False)
    email = db_instance.Column(db_instance.String(100), unique=True, nullable=False)
    password_hash = db_instance.Column(db_instance.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


# CLI Command for Database Initialization
@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    db_instance.drop_all()  # Drops all tables (for resetting)
    db_instance.create_all()  # Creates new tables
    click.echo("Database initialized successfully.")


# Register CLI commands
app.cli.add_command(init_db_command)


# Middleware to load user before requests
@app.before_request
def load_user():
    user_id = session.get("user_id")
    g.user = User.query.get(user_id) if user_id else None


# Routes for products
@app.route("/products.json")
def products_index():
    return jsonify(db.products_all())


@app.route("/products/<int:id>.json", methods=["GET"])
def products_show(id):
    product = db.products_find_by_id(id)
    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404


@app.route("/products/<int:id>.json", methods=["PATCH"])
def products_update(id):
    product = db.products_find_by_id(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    name = request.json.get("name", product["name"])
    image_url = request.json.get("image_url", product["image_url"])
    description = request.json.get("description", product["description"])
    price = request.json.get("price", product["price"])
    quantity = request.json.get("quantity", product["quantity"])
    db.products_update_by_id(id, name, price, description, quantity)
    return jsonify({"message": "Product updated successfully"})


@app.route("/products.json", methods=["POST"])
def create_product():
    data = request.json
    name = data.get("name")
    price = data.get("price")
    description = data.get("description")
    quantity = data.get("quantity")
    categories = data.get("categories", [])
    image_urls = data.get("image_urls", [])
    if not all([name, price, description, quantity]):
        return jsonify({"error": "Missing required fields"}), 400
    db.products_create(name, price, description, quantity, categories, image_urls)
    return jsonify({"message": "Product created successfully"}), 201


@app.route("/products/<int:id>.json", methods=["DELETE"])
def products_destroy(id):
    if db.products_destroy_by_id(id):
        return jsonify({"message": "Product deleted successfully"})
    return jsonify({"error": "Product not found"}), 404


# Routes for user authentication
@app.route("/users", methods=["POST"])
def users_create():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    if not all([name, email, password]):
        return jsonify({"error": "Missing required fields"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(name=name, email=email, password_hash=hashed_password)
    try:
        db_instance.session.add(user)
        db_instance.session.commit()
        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        return jsonify({"error": "A user with this email already exists"}), 400


@app.route("/sessions", methods=["POST"])
def sessions_create():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    if not all([email, password]):
        return jsonify({"error": "Missing required fields"}), 400

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        session["user_id"] = user.id
        return jsonify(
            {"message": "Logged in successfully", "user": {"id": user.id, "name": user.name, "email": user.email}}
        )
    return jsonify({"error": "Invalid email or password"}), 401


@app.route("/sessions", methods=["DELETE"])
def sessions_destroy():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out successfully"}), 200


@app.route("/me", methods=["GET"])
def current_user():
    if g.user:
        return jsonify({"name": g.user.name, "email": g.user.email})
    return jsonify({"error": "Unauthorized"}), 401


# Main entry point
if __name__ == "__main__":
    app.run(debug=True)
