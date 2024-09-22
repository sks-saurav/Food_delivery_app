import sqlite3

class User:
    """
    Represents a user in the food delivery system.

    """

    def __init__(self, user_id, name, address, phone_number):
        """
        Initializes a new User object.

        Args:
            user_id (int): The unique identifier for the user.
            name (str): The user's name.
            address (str): The user's delivery address.
            phone_number (str): The user's phone number.
        """
        self.id = user_id
        self.name = name
        self.address = address
        self.phone_number = phone_number


class UserManager:
    """
    Manages user operations such as registration and retrieval.

    """

    def __init__(self, db_connection, redis_connection):
        """
        Initializes a new UserManager object with database and Redis connections.

        Args:
            db_connection (sqlite3.Connection): SQLite database connection.
            redis_connection (redis.Redis): Redis connection for caching.
        """
        self.conn = db_connection
        self.redis = redis_connection

    def register_user(self, name, address, phone_number):
        """
        Registers a new user in the system.

        Args:
            name (str): The user's name.
            address (str): The user's delivery address.
            phone_number (str): The user's phone number.

        Raises:
            ValueError: If a user with the same phone number already exists in the system.
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute('INSERT INTO users (name, address, phone_number) VALUES (?, ?, ?)',
                           (name, address, phone_number))
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            raise ValueError(f"User with phone number {phone_number} already exists.")

    def get_user(self, user_id):
        """
        Retrieves a user by their user ID.

        Args:
            user_id (int): The unique identifier for the user.

        Returns:
            tuple: A tuple containing the user's information (id, name, address, phone_number),
                   or None if the user is not found.
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return cursor.fetchone()
