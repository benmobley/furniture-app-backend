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
          category TEXT,
        );
        """
    )
    conn.commit()
    print("Table created successfully")

    products_seed_data = [
        ("Chair", "Sit on it", 400, "Dining Room"),
        ("Table", "Put stuff on here", 768, "Dining Room"),
        ("Desk", "Study here", 200, "Office"),
    ]
    conn.executemany(
        """
        INSERT INTO products (name, description, price, category)
        VALUES (?,?,?,?)
        """,
        products_seed_data,
    )
    conn.commit()
    print("Seed data created successfully")

    conn.close()


if __name__ == "__main__":
    initial_setup()