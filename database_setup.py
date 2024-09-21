import sqlite3

def get_db_connection():
    """Establishes and returns a connection to the SQLite database."""
    conn = sqlite3.connect('food_delivery.db')
    conn.row_factory = sqlite3.Row
    return conn

def setup_tables(connection):
    """Creates all the necessary tables for the food delivery service backend."""
    cursor = connection.cursor()

    cursor.executescript('''
            -- users table
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            phone_number TEXT NOT NULL UNIQUE
        );
        
        -- riders table
        CREATE TABLE riders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            vehicle_details TEXT,
            current_latitude REAL,
            current_longitude REAL
        );
        
        -- restaurants table
        CREATE TABLE restaurants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            cuisine TEXT NOT NULL,
            latitude REAL,
            longitude REAL
        );
        
        -- menu_items table
        CREATE TABLE menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                restaurant_id INTEGER,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                category TEXT,
                FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
            );
            
            -- orders table
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                restaurant_id INTEGER,
                rider_id INTEGER,
                menu_items TEXT, -- A JSON list of menu items
                status TEXT NOT NULL,
                delivery_time_estimate INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (restaurant_id) REFERENCES restaurants(id),
                FOREIGN KEY (rider_id) REFERENCES riders(id)
            );
    ''')

    connection.commit()
    connection.close()
    print("Database tables created successfully!")

