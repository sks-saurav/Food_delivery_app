import json

class MenuItem:
    """
    Represents a menu item in a restaurant.

    """

    def __init__(self, item_id, name, price, category):
        """
        Initializes a new MenuItem object.

        Args:
            item_id (int): The unique identifier for the menu item.
            name (str): The name of the menu item.
            price (float): The price of the menu item.
            category (str): The category of the menu item (e.g., appetizer, main course).
        """
        self.id = item_id
        self.name = name
        self.price = price
        self.category = category


class Restaurant:
    """
    Represents a restaurant in the food delivery system.

    """

    def __init__(self, restaurant_id, name, address, cuisine, location, menu):
        """
        Initializes a new Restaurant object.

        Args:
            restaurant_id (int): The unique identifier for the restaurant.
            name (str): The name of the restaurant.
            address (str): The address of the restaurant.
            cuisine (str): The cuisine type of the restaurant.
            location (tuple): The geographical location of the restaurant (latitude, longitude).
            menu (list of MenuItem): A list of menu items offered by the restaurant.
        """
        self.id = restaurant_id
        self.name = name
        self.address = address
        self.cuisine = cuisine
        self.location = location  # (lat, long)
        self.menu = menu


class RestaurantManager:
    """
    Manages restaurant operations including registration, restaurant suggestions, and menu retrieval.

    Attributes:
        conn (sqlite3.Connection): SQLite database connection.
        redis (redis.Redis): Redis connection for caching purposes.
    """

    def __init__(self, db_connection, redis_connection):
        """
        Initializes a new RestaurantManager object with database and Redis connections.

        Args:
            db_connection (sqlite3.Connection): SQLite database connection.
            redis_connection (redis.Redis): Redis connection for caching.
        """
        self.conn = db_connection
        self.redis = redis_connection

    def register_restaurant(self, name, address, cuisine, location, menu):
        """
        Registers a new restaurant and its menu in the system.

        Args:
            name (str): The name of the restaurant.
            address (str): The address of the restaurant.
            cuisine (str): The type of cuisine the restaurant offers.
            location (tuple): The restaurant's location as a tuple (latitude, longitude).
            menu (list of MenuItem): A list of menu items offered by the restaurant.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO restaurants (name, address, cuisine, latitude, longitude) VALUES (?, ?, ?, ?, ?)',
            (name, address, cuisine, location[0], location[1])
        )
        restaurant_id = cursor.lastrowid

        for item in menu:
            cursor.execute(
                'INSERT INTO menu_items (restaurant_id, name, price, category) VALUES (?, ?, ?, ?)',
                (restaurant_id, item.name, item.price, item.category)
            )
        self.conn.commit()

        # Clear cache for this cuisine type
        self.redis.delete(f"restaurants:suggestions:{cuisine}")

    def suggest_restaurants(self, cuisine, max_delivery_time, user_location):
        """
        Suggests restaurants based on cuisine type and estimated delivery time.

        Args:
            cuisine (str): The type of cuisine the user is interested in.
            max_delivery_time (float): The maximum delivery time in minutes.
            user_location (tuple): The user's location as a tuple (latitude, longitude).

        Returns:
            list: A list of suggested restaurants matching the criteria.
        """
        cache_key = f"restaurants:suggestions:{cuisine}"
        cached_data = self.redis.get(cache_key)

        if cached_data:
            print("Fetching suggestions from cache...")
            return json.loads(cached_data)

        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM restaurants WHERE cuisine = ?', (cuisine,))
        restaurants = cursor.fetchall()

        suggested_restaurants = []
        for restaurant in restaurants:
            restaurant_location = (restaurant["latitude"], restaurant["longitude"])
            delivery_time_estimate = self._estimate_delivery_time(restaurant_location, user_location)
            if delivery_time_estimate <= max_delivery_time:
                suggested_restaurants.append(restaurant)

        # Cache the suggestions
        self.redis.set(cache_key, json.dumps(suggested_restaurants), ex=3600)  # Cache for 1 hour
        return suggested_restaurants

    def _estimate_delivery_time(self, restaurant_location, user_location):
        """
        Estimates delivery time based on the distance between the restaurant and the user.

        Args:
            restaurant_location (tuple): The location of the restaurant (latitude, longitude).
            user_location (tuple): The user's location (latitude, longitude).

        Returns:
            float: The estimated delivery time in minutes.
        """
        distance = ((restaurant_location[0] - user_location[0]) ** 2 +
                    (restaurant_location[1] - user_location[1]) ** 2) ** 0.5
        return distance * 10  # Example: 10 minutes per unit distance

    def get_menu(self, restaurant_id):
        """
        Retrieves the menu of a restaurant.

        Args:
            restaurant_id (int): The unique identifier for the restaurant.

        Returns:
            list: A list of menu items offered by the restaurant.
        """
        cache_key = f"menu:{restaurant_id}"
        cached_menu = self.redis.get(cache_key)

        if cached_menu:
            print("Fetching menu from cache...")
            return json.loads(cached_menu)

        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM menu_items WHERE restaurant_id = ?', (restaurant_id,))
        menu_items = cursor.fetchall()

        # Cache the menu items
        self.redis.set(cache_key, json.dumps(menu_items), ex=3600)  # Cache for 1 hour
        return menu_items
