import sqlite3

def connect_to_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def initial_setup():
    conn = connect_to_db()
    conn.execute(
        """
        DROP TABLE IF EXISTS products;
        """
    )
    conn.execute(
        """
        CREATE TABLE products (
          id INTEGER PRIMARY KEY NOT NULL,
          name TEXT,
          image_url TEXT,
          description TEXT,
          price INTEGER,
          category TEXT,
          tax FLOAT,
          total INTEGER  
        );
        """
    )
    conn.commit()
    print("Table created successfully")

    products_seed_data = [
        ("Chair", "image.jpg", "Sit on it", 400, "Dining Room", 0.1, 440),
        ("Table", "image.jpg", "Put stuff on here", 768, "Dining Room", 0.1, 844.8),
        ("Desk", "image.jpg", "Study here", 200, "Office", 0.1, 220),
    ]
    conn.executemany(
        """
        INSERT INTO products (name, image_url, description, price, category, tax, total)
        VALUES (?,?,?,?,?,?,?)
        """,
        products_seed_data,
    )
    conn.commit()
    print("Seed data created successfully")

    conn.close()

def products_all():
    conn = connect_to_db()
    rows = conn.execute(
        """
        SELECT * FROM products
        """
    ).fetchall()
    conn.close()  # Close the connection to avoid resource leaks
    return [dict(row) for row in rows]

def products_update_by_id(id, name, image_url, description, price, category, tax, total):
    conn = connect_to_db()
    row = conn.execute(
        """
        UPDATE products SET name = ?, image_url = ?, description = ?, price = ?, category = ?, tax = ?, total = ?
        WHERE id = ?
        RETURNING *
        """,
        (name, image_url, description, price, category, tax, total, id)
    ).fetchone()
    conn.commit()
    return dict(row)


def products_create(id, name, image_url, description, price, category, tax, total):
    conn = connect_to_db()
    row = conn.execute(
        """
        INSERT INTO products (name, image_url, description, price, category, tax, total)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        RETURNING *
        """,
        (name, image_url, description, price, category, tax, total),
    ).fetchone()
    conn.commit()
    

def products_find_by_id(id):
    conn = connect_to_db()
    row = conn.execute(
        """
        SELECT * FROM products
        WHERE id = ?
        """,
        (id,),
    ).fetchone()
    return dict(row)

def products_destroy_by_id(id):
    conn = connect_to_db()
    row = conn.execute(
        """
        DELETE from products
        WHERE id = ?
        """,
        (id,),
    )
    conn.commit()
    return {"message": "Product destroyed successfully"}

if __name__ == "__main__":
    initial_setup()