class Rider:
    """
    Represents a rider in the food delivery system.

    """

    def __init__(self, rider_id, name, vehicle_details, current_location):
        """
        Initializes a new Rider object.

        Args:
            rider_id (int): The unique identifier for the rider.
            name (str): The rider's name.
            vehicle_details (str): Details about the rider's vehicle.
            current_location (tuple): The rider's current location as a tuple (latitude, longitude).
        """
        self.rider_id = rider_id
        self.name = name
        self.vehicle_details = vehicle_details
        self.current_location = current_location  # (lat, long)


class RiderManager:
    """
    Manages rider operations such as registration, location updates, and finding the nearest rider.
    """

    def __init__(self, db_connection, redis_connection):
        """
        Initializes a new RiderManager object with database and Redis connections.

        Args:
            db_connection (sqlite3.Connection): SQLite database connection.
            redis_connection (redis.Redis): Redis connection for caching.
        """
        self.conn = db_connection
        self.redis = redis_connection

    def register_rider(self, name, vehicle_details, current_location):
        """
        Registers a new rider in the system.

        Args:
            name (str): The rider's name.
            vehicle_details (str): Details about the rider's vehicle.
            current_location (tuple): The rider's current location as a tuple (latitude, longitude).
        """
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO riders (name, vehicle_details, current_latitude, current_longitude) VALUES (?, ?, ?, ?)',
            (name, vehicle_details, current_location[0], current_location[1])
        )
        self.conn.commit()

    def update_rider_location(self, rider_id, new_location):
        """
        Updates the current location of a rider.

        Args:
            rider_id (int): The unique identifier for the rider.
            new_location (tuple): The new location of the rider as a tuple (latitude, longitude).
        """
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE riders SET current_latitude = ?, current_longitude = ? WHERE id = ?',
            (new_location[0], new_location[1], rider_id)
        )
        self.conn.commit()

    def get_nearest_rider(self, restaurant_location):
        """
        Finds the nearest rider to a given restaurant location.

        Args:
            restaurant_location (tuple): The location of the restaurant as a tuple (latitude, longitude).

        Returns:
            dict: A dictionary representing the nearest rider's details or None if no riders are found.
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM riders')
        riders = cursor.fetchall()

        nearest_rider = None
        min_distance = float('inf')
        for rider in riders:
            rider_location = (rider["current_latitude"], rider["current_longitude"])
            distance = self._calculate_distance(restaurant_location, rider_location)
            if distance < min_distance:
                min_distance = distance
                nearest_rider = rider
        return nearest_rider

    def _calculate_distance(self, location1, location2):
        """
        Calculates the Euclidean distance between two geographical points.

        Args:
            location1 (tuple): The first location as a tuple (latitude, longitude).
            location2 (tuple): The second location as a tuple (latitude, longitude).

        Returns:
            float: The calculated distance between the two points.
        """
        lat1, lon1 = location1
        lat2, lon2 = location2
        return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5
