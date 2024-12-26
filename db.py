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
          description TEXT,
          price INTEGER,
          category TEXT
        );
        """
    )
    conn.commit()
    print("Table created successfully")

    photos_seed_data = [
        ("Chair", "Sit on it", 400, "Dining Room"),
        ("Table", "Put stuff on here", 768, "Dining Room"),
        ("Desk", "Study here", 200, "Office"),
    ]
    conn.executemany(
        """
        INSERT INTO products (name, description, price, category)
        VALUES (?,?,?,?)
        """,
        ps_seed_data,
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

def photos_update_by_id(id, name, width, height):
    conn = connect_to_db()
    row = conn.execute(
        """
        UPDATE photos SET name = ?, width = ?, height = ?
        WHERE id = ?
        RETURNING *
        """,
        (name, width, height, id),
    ).fetchone()
    conn.commit()
    return dict(row)

def products_update_by_id(id, name, description, price, category):
    conn = connect_to_db()
    row = conn.execute(
        """
        UPDATE products SET name = ?, description = ?, price = ?, category = ?
        WHERE id = ?
        RETURNING *
        """,
        (name, description, price, category, id),
    ).fetchone()
    conn.commit()
    return dict(row)


def products_create(name, description, price, category):
    conn = connect_to_db()
    row = conn.execute(
        """
        INSERT INTO products (name, description, price, category)
        VALUES (?, ?, ?, ?)
        RETURNING *
        """,
        (name, description, price, category),
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

if __name__ == "__main__":
    initial_setup()