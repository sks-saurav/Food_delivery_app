import sqlite3

class User:
    def __init__(self, user_id, name, address, phone_number):
        self.id = user_id
        self.name = name
        self.address = address
        self.phone_number = phone_number

class UserManager:
    def __init__(self, db_connection, redis_connection):
        self.conn = db_connection
        self.redis = redis_connection

    def register_user(self, name, address, phone_number):
        cursor = self.conn.cursor()
        try:
            cursor.execute('INSERT INTO users (name, address, phone_number) VALUES (?, ?, ?)',
                           (name, address, phone_number))
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            raise ValueError(f"User with phone number {phone_number} already exists.")

    def get_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return cursor.fetchone()


