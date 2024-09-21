import json

class Order:
    def __init__(self, order_id, user_id, restaurant_id, rider_id, menu_items, status, delivery_time_estimate):
        self.id = order_id
        self.user_id = user_id
        self.restaurant_id = restaurant_id
        self.rider_id = rider_id
        self.menu_items = menu_items
        self.status = status
        self.delivery_time_estimate = delivery_time_estimate

class OrderManager:
    def __init__(self, db_connection, redis_connection):
        self.conn = db_connection
        self.redis = redis_connection

    def place_order(self, user_id, restaurant_id, menu_items, rider_id, delivery_time_estimate):
        cursor = self.conn.cursor()
        menu_items_json = json.dumps([item.__dict__ for item in menu_items])
        cursor.execute('INSERT INTO orders (user_id, restaurant_id, rider_id, menu_items, status, delivery_time_estimate) VALUES (?, ?, ?, ?, ?, ?)',
                       (user_id, restaurant_id, rider_id, menu_items_json, "Pending", delivery_time_estimate))
        self.conn.commit()

        # Invalidate the cache for both the user and rider's order history
        self.redis.delete(f"user_order_history:{user_id}")
        self.redis.delete(f"rider_order_history:{rider_id}")

    def get_order_history_by_user(self, user_id):
        # Check if user order history is cached
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
        # Check if rider order history is cached
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
