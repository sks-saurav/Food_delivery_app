import json

class MenuItem:
    def __init__(self, item_id, name, price, category):
        self.id = item_id
        self.name = name
        self.price = price
        self.category = category

class Restaurant:
    def __init__(self, restaurant_id, name, address, cuisine, location, menu):
        self.id = restaurant_id
        self.name = name
        self.address = address
        self.cuisine = cuisine
        self.location = location  # (lat, long)
        self.menu = menu

class RestaurantManager:
    def __init__(self, db_connection, redis_connection):
        self.conn = db_connection
        self.redis = redis_connection

    def register_restaurant(self, name, address, cuisine, location, menu):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO restaurants (name, address, cuisine, latitude, longitude) VALUES (?, ?, ?, ?, ?)',
                       (name, address, cuisine, location[0], location[1]))
        restaurant_id = cursor.lastrowid

        for item in menu:
            cursor.execute('INSERT INTO menu_items (restaurant_id, name, price, category) VALUES (?, ?, ?, ?)',
                           (restaurant_id, item.name, item.price, item.category))
        self.conn.commit()

        # Clear cache for this cuisine type
        self.redis.delete(f"restaurants:suggestions:{cuisine}")

    def suggest_restaurants(self, cuisine, max_delivery_time, user_location):
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
        # Use distance to estimate delivery time
        distance = ((restaurant_location[0] - user_location[0]) ** 2 + (restaurant_location[1] - user_location[1]) ** 2) ** 0.5
        return distance * 10  # Example: 10 minutes per unit distance

    def get_menu(self, restaurant_id):
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
