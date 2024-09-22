# Food Delivery Backend

## Introduction

This project is a simple backend for a food delivery service, similar to platforms like Swiggy and Zomato. The app is implemented in Python using SQLite as the database. The backend supports basic functionality including user registration, rider registration, restaurant management, menu display, order placement, and tracking.

The architecture is designed to handle:
- User, Rider, and Restaurant registrations
- Suggesting restaurants based on cuisine and delivery time
- Placing orders and assigning riders based on proximity
- Viewing order history for users and riders

It is built with scalability in mind, and although SQLite is used for this prototype, the design can be migrated to more scalable databases like PostgreSQL or MySQL.

## Features

1. **User Registration**: Allows users to register with their details.
2. **Rider Registration**: Riders can register and update their locations.
3. **Restaurant Registration**: Restaurants can be added with their details including cuisine type and menu.
4. **Restaurant Suggestions**: Users can search for restaurants based on the cuisine type and the time they need food delivered.
5. **Menu Display**: Displays a restaurant's menu items.
6. **Order Management**: Users can place an order, and the nearest rider is assigned to the delivery.
7. **Order History**: Users and riders can view their order history.
8. **Rider Location Updates**: Riders can update their current location to be considered for nearby orders.

## Database

The database schema consists of tables for:
- **Users**
  - id INTEGER PRIMARY KEY AUTOINCREMENT,
  - name TEXT NOT NULL,
  - address TEXT NOT NULL,
  - phone_number TEXT NOT NULL UNIQUE
- **Riders**
    - id INTEGER PRIMARY KEY AUTOINCREMENT,
    - name TEXT NOT NULL,
    - vehicle_details TEXT,
    - current_latitude REAL,
    - current_longitude REAL
- **Restaurants**
    - id INTEGER PRIMARY KEY AUTOINCREMENT,
    - name TEXT NOT NULL,
    - address TEXT NOT NULL,
    - cuisine TEXT NOT NULL,
    - latitude REAL,
    - longitude REAL
- **Menu**
    - id INTEGER PRIMARY KEY AUTOINCREMENT,
    - restaurant_id INTEGER,
    - name TEXT NOT NULL,
    - price REAL NOT NULL,
    - category TEXT,
    - FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
- **Orders**
    - id INTEGER PRIMARY KEY AUTOINCREMENT,
    - user_id INTEGER,
    - restaurant_id INTEGER,
    - rider_id INTEGER,
    - menu_items TEXT, -- A JSON list of menu items
    - status TEXT NOT NULL,
    - delivery_time_estimate INTEGER,
    - FOREIGN KEY (user_id) REFERENCES users(id),
    - FOREIGN KEY (restaurant_id) REFERENCES restaurants(id),
    - FOREIGN KEY (rider_id) REFERENCES riders(id)
