class Rider:
    def __init__(self, rider_id, name, vehicle_details, current_location):
        self.id = rider_id
        self.name = name
        self.vehicle_details = vehicle_details
        self.current_location = current_location  # (lat, long)

class RiderManager:
    def __init__(self, db_connection, redis_connection):
        self.conn = db_connection
        self.redis = redis_connection

    def register_rider(self, name, vehicle_details, current_location):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO riders (name, vehicle_details, current_latitude, current_longitude) VALUES (?, ?, ?, ?)',
                       (name, vehicle_details, current_location[0], current_location[1]))
        self.conn.commit()

    def update_rider_location(self, rider_id, new_location):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE riders SET current_latitude = ?, current_longitude = ? WHERE id = ?',
                       (new_location[0], new_location[1], rider_id))
        self.conn.commit()

    def get_nearest_rider(self, restaurant_location):
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
        # Simplified distance calculation (you can replace with a more accurate method)
        lat1, lon1 = location1
        lat2, lon2 = location2
        return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5
