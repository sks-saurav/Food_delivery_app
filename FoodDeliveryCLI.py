from cache_setup import get_redis_connection
from users import UserManager
from rider import RiderManager
from restaurant import RestaurantManager, MenuItem
from order import OrderManager
from database_setup import get_db_connection, setup_tables


class FoodDeliveryCLI:
    def __init__(self):
        self.db_conn = get_db_connection()
        self.redis_conn = get_redis_connection()
        setup_tables(self.db_conn)
        self.user_manager = UserManager(self.db_conn, self.redis_conn)
        self.rider_manager = RiderManager(self.db_conn, self.redis_conn)
        self.restaurant_manager = RestaurantManager(self.db_conn, self.redis_conn)
        self.order_manager = OrderManager(self.db_conn, self.redis_conn)

    def display_menu(self):
        print("\nFood Delivery App")
        print("-----------------")
        print("1. Register User")
        print("2. Register Rider")
        print("3. Register Restaurant")
        print("4. Suggest Restaurants")
        print("5. Place Order")
        print("6. Update Rider Location")
        print("7. View User Order History")
        print("8. View Rider Order History")
        print("9. Exit")

    def run(self):
        while True:
            self.display_menu()
            choice = input("\nEnter choice: ")
            if choice == "1":
                self.register_user()
            elif choice == "2":
                self.register_rider()
            elif choice == "3":
                self.register_restaurant()
            elif choice == "4":
                self.suggest_restaurants()
            elif choice == "5":
                self.place_order()
            elif choice == "6":
                self.update_rider_location()
            elif choice == "7":
                self.view_user_order_history()
            elif choice == "8":
                self.view_rider_order_history()
            elif choice == "9":
                break
            else:
                print("Invalid choice. Please try again.")

    def register_user(self):
        name = input("Enter user name: ")
        address = input("Enter user address: ")
        phone_number = input("Enter phone number: ")
        try:
            self.user_manager.register_user(name, address, phone_number)
            print(f"User {name} registered successfully.")
        except ValueError as e:
            print(e)

    def register_rider(self):
        name = input("Enter rider name: ")
        vehicle_details = input("Enter vehicle details: ")
        lat = float(input("Enter current latitude: "))
        lon = float(input("Enter current longitude: "))
        self.rider_manager.register_rider(name, vehicle_details, (lat, lon))
        print(f"Rider {name} registered successfully.")

    def register_restaurant(self):
        name = input("Enter restaurant name: ")
        address = input("Enter restaurant address: ")
        cuisine = input("Enter cuisine type: ")
        lat = float(input("Enter restaurant latitude: "))
        lon = float(input("Enter restaurant longitude: "))

        menu = []
        while True:
            item_name = input("Enter menu item name (or type 'done' to finish): ")
            if item_name == "done":
                break
            price = float(input("Enter price: "))
            category = input("Enter category: ")
            menu.append(MenuItem(None, item_name, price, category))

        self.restaurant_manager.register_restaurant(name, address, cuisine, (lat, lon), menu)
        print(f"Restaurant {name} registered successfully.")

    def suggest_restaurants(self):
        cuisine = input("Enter preferred cuisine: ")
        max_delivery_time = int(input("Enter max delivery time in minutes: "))
        user_lat = float(input("Enter your latitude: "))
        user_lon = float(input("Enter your longitude: "))
        restaurants = self.restaurant_manager.suggest_restaurants(cuisine, max_delivery_time, (user_lat, user_lon))
        if restaurants:
            print("\nSuggested Restaurants:")
            for restaurant in restaurants:
                print(f"- {restaurant['name']} at {restaurant['address']}")
        else:
            print("No restaurants found.")

    def place_order(self):
        user_id = int(input("Enter your user ID: "))
        restaurant_id = int(input("Enter restaurant ID: "))

        # Show restaurant menu
        menu_items = self.restaurant_manager.get_menu(restaurant_id)
        if not menu_items:
            print("No menu found for this restaurant.")
            return

        print("\nMenu:")
        for item in menu_items:
            print(f"{item['id']}. {item['name']} - ${item['price']} ({item['category']})")

        selected_items = []
        while True:
            item_id = input("Enter item ID to order (or type 'done' to finish): ")
            if item_id == "done":
                break
            item = next((i for i in menu_items if i["id"] == int(item_id)), None)
            if item:
                selected_items.append(MenuItem(item['id'], item['name'], item['price'], item['category']))

        if not selected_items:
            print("No items selected.")
            return

        # Find the nearest rider
        restaurant_location = (menu_items[0]['latitude'], menu_items[0]['longitude'])
        nearest_rider = self.rider_manager.get_nearest_rider(restaurant_location)

        if not nearest_rider:
            print("No available riders found.")
            return

        delivery_time_estimate = self.restaurant_manager._estimate_delivery_time(
            restaurant_location, (nearest_rider['current_latitude'], nearest_rider['current_longitude'])
        )

        # Place order
        self.order_manager.place_order(user_id, restaurant_id, selected_items, nearest_rider['id'], delivery_time_estimate)
        print("Order placed successfully.")

    def update_rider_location(self):
        rider_id = int(input("Enter rider ID: "))
        new_lat = float(input("Enter new latitude: "))
        new_lon = float(input("Enter new longitude: "))
        self.rider_manager.update_rider_location(rider_id, (new_lat, new_lon))
        print("Rider location updated successfully.")

    def view_user_order_history(self):
        user_id = int(input("Enter user ID: "))
        orders = self.order_manager.get_order_history_by_user(user_id)
        if orders:
            print("\nOrder History:")
            for order in orders:
                print(f"Order {order['id']} from Restaurant {order['restaurant_id']} - Status: {order['status']}")
        else:
            print("No order history found.")

    def view_rider_order_history(self):
        rider_id = int(input("Enter rider ID: "))
        orders = self.order_manager.get_order_history_by_rider(rider_id)
        if orders:
            print("\nOrder History:")
            for order in orders:
                print(f"Order {order['id']} for User {order['user_id']} - Status: {order['status']}")
        else:
            print("No order history found.")


# Run the CLI
if __name__ == "__main__":
    app = FoodDeliveryCLI()
    app.run()
