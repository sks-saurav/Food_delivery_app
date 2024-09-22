import json

class Order:
    """
    Represents an order in the food delivery system.
    """

    def __init__(self, order_id, user_id, restaurant_id, rider_id, menu_items, status, delivery_time_estimate):
        """
        Initializes a new Order object.

        Args:
            order_id (int): The unique identifier for the order.
            user_id (int): The ID of the user placing the order.
            restaurant_id (int): The ID of the restaurant where the order is placed.
            rider_id (int): The ID of the rider assigned to deliver the order.
            menu_items (list of MenuItem): A list of menu items included in the order.
            status (str): The current status of the order.
            delivery_time_estimate (float): The estimated delivery time in minutes.
        """
        self.id = order_id
        self.user_id = user_id
        self.restaurant_id = restaurant_id
        self.rider_id = rider_id
        self.menu_items = menu_items
        self.status = status
        self.delivery_time_estimate = delivery_time_estimate


class OrderManager:
    """
    Manages order-related operations such as placing orders and retrieving order history.
    """

    def __init__(self, db_connection, redis_connection):
        """
        Initializes a new OrderManager object with database and Redis connections.

        Args:
            db_connection (sqlite3.Connection): SQLite database connection.
            redis_connection (redis.Redis): Redis connection for caching.
        """
        self.conn = db_connection
        self.redis = redis_connection

    def place_order(self, user_id, restaurant_id, menu_items, rider_id, delivery_time_estimate):
        """
        Places a new order in the system.

        Args:
            user_id (int): The ID of the user placing the order.
            restaurant_id (int): The ID of the restaurant where the order is placed.
            menu_items (list of MenuItem): A list of menu items included in the order.
            rider_id (int): The ID of the rider assigned to deliver the order.
            delivery_time_estimate (float): The estimated delivery time in minutes.
        """
        cursor = self.conn.cursor()
        menu_items_json = json.dumps([item.__dict__ for item in menu_items])
        cursor.execute(
            'INSERT INTO orders (user_id, restaurant_id, rider_id, menu_items, status, delivery_time_estimate) VALUES (?, ?, ?, ?, ?, ?)',
            (user_id, restaurant_id, rider_id, menu_items_json, "Pending", delivery_time_estimate)
        )
        self.conn.commit()

        # Invalidate the cache for both the user and rider's order history
        self.redis.delete(f"user_order_history:{user_id}")
        self.redis.delete(f"rider_order_history:{rider_id}")

    def get_order_history_by_user(self, user_id):
        """
        Retrieves the order history for a specific user.

        Args:
            user_id (int): The ID of the user whose order history is to be retrieved.

        Returns:
            list: A list of orders made by the user.
        """
        cache_key = f"user_order_history:{user_id}"
        cached_orders = self.redis.get(cache_key)

        if cached_orders:
            print("Fetching user order history from cache...")
            return json.loads(cached_orders)

        # If not cached, retrieve from the database
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE user_id = ?', (user_id,))
        orders = cursor.fetchall()

        # Cache the user order history
        self.redis.set(cache_key, json.dumps([dict(order) for order in orders]), ex=3600)  # Cache for 1 hour
        return orders

    def get_order_history_by_rider(self, rider_id):
        """
        Retrieves the order history for a specific rider.

        Args:
            rider_id (int): The ID of the rider whose order history is to be retrieved.

        Returns:
            list: A list of orders delivered by the rider.
        """
        cache_key = f"rider_order_history:{rider_id}"
        cached_orders = self.redis.get(cache_key)

        if cached_orders:
            print("Fetching rider order history from cache...")
            return json.loads(cached_orders)

        # If not cached, retrieve from the database
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE rider_id = ?', (rider_id,))
        orders = cursor.fetchall()

        # Cache the rider order history
        self.redis.set(cache_key, json.dumps([dict(order) for order in orders]), ex=3600)  # Cache for 1 hour
        return orders
