import sqlite3
from datetime import datetime
import bcrypt

def connect_to_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def initial_setup():
    conn = connect_to_db()
    # Drop existing tables if they exist
    tables = ['products', 'users', 'orders', 'carted_products', 'categories', 'category_products', 'images']
    for table in tables:
        conn.execute(f"DROP TABLE IF EXISTS {table};")

    # Create Users table
    conn.execute("""
    CREATE TABLE users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT,
      email TEXT UNIQUE,
      password_digest TEXT,
      admin BOOLEAN DEFAULT FALSE,
      created_at DATETIME,
      updated_at DATETIME
    );
    """)

    # Create Categories table
    conn.execute("""
    CREATE TABLE categories (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT,
      created_at DATETIME,
      updated_at DATETIME
    );
    """)

    # Create Products table
    conn.execute("""
    CREATE TABLE products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT,
      price INTEGER,
      description TEXT,
      quantity INTEGER,
      created_at DATETIME,
      updated_at DATETIME
    );
    """)

    # Create Orders table
    conn.execute("""
    CREATE TABLE orders (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER,
      subtotal DECIMAL,
      tax DECIMAL,
      total DECIMAL,
      created_at DATETIME,
      updated_at DATETIME,
      FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)

    # Create CartedProducts table
    conn.execute("""
    CREATE TABLE carted_products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER,
      product_id INTEGER,
      quantity INTEGER,
      status TEXT,
      order_id INTEGER,
      created_at DATETIME,
      updated_at DATETIME,
      FOREIGN KEY(user_id) REFERENCES users(id),
      FOREIGN KEY(product_id) REFERENCES products(id),
      FOREIGN KEY(order_id) REFERENCES orders(id)
    );
    """)

    # Create CategoryProducts table
    conn.execute("""
    CREATE TABLE category_products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      product_id INTEGER,
      category_id INTEGER,
      created_at DATETIME,
      updated_at DATETIME,
      FOREIGN KEY(product_id) REFERENCES products(id),
      FOREIGN KEY(category_id) REFERENCES categories(id)
    );
    """)

    # Create Images table
    conn.execute("""
    CREATE TABLE images (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      url TEXT,
      product_id INTEGER,
      created_at DATETIME,
      updated_at DATETIME,
      FOREIGN KEY(product_id) REFERENCES products(id)
    );
    """)

    users_seed_data = [
        ("Alice", "alice@example.com", "hashed_password", False, datetime.now(), datetime.now()),
        ("Bob", "bob@example.com", "hashed_password", True, datetime.now(), datetime.now())
    ]
    categories_seed_data = [
        ("Electronics", datetime.now(), datetime.now()),
        ("Furniture", datetime.now(), datetime.now())
    ]
    products_seed_data = [
        ("Laptop", 1000, "High-performance laptop", 5, datetime.now(), datetime.now()),
        ("Chair", 150, "Comfortable office chair", 10, datetime.now(), datetime.now())
    ]
    orders_seed_data = [
        (1, 1150, 50, 1200, datetime.now(), datetime.now()),
        (2, 300, 15, 315, datetime.now(), datetime.now())
    ]
    carted_products_seed_data = [
        (1, 1, 1, "in_cart", None, datetime.now(), datetime.now()),
        (2, 2, 2, "purchased", 2, datetime.now(), datetime.now())
    ]
    category_products_seed_data = [
        (1, 1, datetime.now(), datetime.now()),
        (2, 2, datetime.now(), datetime.now())
    ]
    images_seed_data = [
        ("https://www.techtarget.com/rms/onlineimages/hp_elitebook_mobile.jpg", 1, datetime.now(), datetime.now()),
        ("https://d2bl4mvd8nzejc.cloudfront.net/img/p/2/0/5/205.jpg", 2, datetime.now(), datetime.now())
    ]

    conn.executemany("INSERT INTO users (name, email, password_digest, admin, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)", users_seed_data)
    conn.executemany("INSERT INTO categories (name, created_at, updated_at) VALUES (?, ?, ?)", categories_seed_data)
    conn.executemany("INSERT INTO products (name, price, description, quantity, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)", products_seed_data)
    conn.executemany("INSERT INTO orders (user_id, subtotal, tax, total, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)", orders_seed_data)
    conn.executemany("INSERT INTO carted_products (user_id, product_id, quantity, status, order_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)", carted_products_seed_data)
    conn.executemany("INSERT INTO category_products (product_id, category_id, created_at, updated_at) VALUES (?, ?, ?, ?)", category_products_seed_data)
    conn.executemany("INSERT INTO images (url, product_id, created_at, updated_at) VALUES (?, ?, ?, ?)", images_seed_data)

    conn.commit()
    print("All tables created and seeded successfully")
    conn.close()

def products_all():
    conn = connect_to_db()
    query = """
    SELECT p.id, p.name, p.description, p.price, p.quantity, p.created_at, p.updated_at,
           c.name as category_name, i.url as image_url
    FROM products p
    LEFT JOIN category_products cp ON p.id = cp.product_id
    LEFT JOIN categories c ON cp.category_id = c.id
    LEFT JOIN images i ON p.id = i.product_id
    """
    products = conn.execute(query).fetchall()
    conn.close()
    
    # Organize products data
    product_dict = {}
    for product in products:
        product_id = product["id"]
        if product_id not in product_dict:
            product_dict[product_id] = {
                "id": product["id"],
                "name": product["name"],
                "description": product["description"],
                "price": product["price"],
                "quantity": product["quantity"],
                "created_at": product["created_at"],
                "updated_at": product["updated_at"],
                "categories": set(),
                "images": set()
            }
        if product["category_name"]:
            product_dict[product_id]["categories"].add(product["category_name"])
        if product["image_url"]:
            product_dict[product_id]["images"].add(product["image_url"])

    # Convert set to list for JSON serialization
    final_products = []
    for id, data in product_dict.items():
        data["categories"] = list(data["categories"])
        data["images"] = list(data["images"])
        final_products.append(data)
    
    return final_products


def products_find_by_id(product_id):
    conn = connect_to_db()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    return dict(product) if product else None

def products_create(name, price, description, quantity, categories, image_urls):
    now = datetime.now()
    conn = connect_to_db()
    try:
        # Insert the new product
        cur = conn.cursor()
        cur.execute("INSERT INTO products (name, price, description, quantity, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)", 
                    (name, price, description, quantity, now, now))
        product_id = cur.lastrowid  # Get the ID of the newly inserted product

        # Handle categories
        for category_name in categories:
            # Assume function to get category ID from name
            category_id = get_category_id_by_name(category_name, conn)
            if category_id:
                cur.execute("INSERT INTO category_products (product_id, category_id) VALUES (?, ?)", (product_id, category_id))

        # Handle images
        for image_url in image_urls:
            cur.execute("INSERT INTO images (url, product_id, created_at, updated_at) VALUES (?, ?, ?, ?)", 
                        (image_url, product_id, now, now))

        conn.commit()
    finally:
        conn.close()

def get_category_id_by_name(name, conn):
    category = conn.execute("SELECT id FROM categories WHERE name = ?", (name,)).fetchone()
    return category['id'] if category else None

def products_update_by_id(id, name, price, description, quantity, created_at, updated_at):
    conn = connect_to_db()
    conn.execute("UPDATE products SET name = ?, price = ?, description = ?, quantity = ?, created_at = ?, updated_at = ? WHERE id = ?", (name, price, description, quantity, created_at, updated_at, id))
    conn.commit()
    conn.close()

def products_destroy_by_id(product_id):
    conn = connect_to_db()
    conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

def users_create(name, email, password_digest):
    """Insert a new user into the database."""
    now = datetime.now()
    conn = connect_to_db()
    try:
        conn.execute("""
            INSERT INTO users (name, email, password_digest, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (name, email, password_digest, now, now))
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError("A user with this email already exists")
    finally:
        conn.close()

def users_find_by_email(email):
    """Retrieve a user by their email address."""
    conn = connect_to_db()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return dict(user) if user else None
def hash_password(password):
    """Hash a plain-text password."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def check_password(password, password_digest):
    """Verify a plain-text password against its hashed version."""
    return bcrypt.checkpw(password.encode("utf-8"), password_digest.encode("utf-8"))

if __name__ == "__main__":
    initial_setup()
