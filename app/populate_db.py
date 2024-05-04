import csv
import os
import mysql.connector
from mysql.connector import Error
import time

# MySQL connection configuration
MYSQL_HOST = 'mysql'
MYSQL_USER = 'myuser'
MYSQL_PASSWORD = 'mypassword'
MYSQL_DB = 'mydatabase'

# Create tables SQL queries
CREATE_USER_TABLE = """
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL
)
"""

CREATE_BOOK_TABLE = """
CREATE TABLE IF NOT EXISTS book (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(255) NOT NULL,
    coverimage VARCHAR(255) NOT NULL
)
"""

CREATE_USER_BOOK_LINK_TABLE = """
CREATE TABLE IF NOT EXISTS user_book_link (
    user_id INT,
    book_id INT,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (book_id) REFERENCES book(id)
)
"""

# Function to create tables
def create_tables(connection):
    try:
        cursor = connection.cursor()
        cursor.execute(CREATE_USER_TABLE)
        cursor.execute(CREATE_BOOK_TABLE)
        cursor.execute(CREATE_USER_BOOK_LINK_TABLE)
        connection.commit()
        print("Tables created successfully!")
    except Error as e:
        print("Error creating tables:", e)

# Function to populate user table
def populate_user_table(connection):
    # Sample data for user table
    users = [
        ("user1", "password1", "John Doe"),
        ("user2", "password2", "Jane Smith"),
        ("user3", "password3", "Alice Johnson")
    ]

    try:
        cursor = connection.cursor()
        for user in users:
            cursor.execute("INSERT INTO user (username, password, name) VALUES (%s, %s, %s)", user)
        connection.commit()
        print("User table populated successfully!")
    except Error as e:
        print("Error inserting into user table:", e)

# Function to populate book table
def populate_book_table(connection):
    # Sample data for book table
    with open('static/data/raw_book_db.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO book (title, author, isbn, coverimage) VALUES (%s, %s, %s, %s)",
                           (row['Title'], row['Author'], row['ISBN'], f"static/data/{row['ISBN']}.jpg"))
    connection.commit()
    print("Book table populated successfully!")

# Function to populate user-book-link table
def populate_user_book_link_table(connection):
    # Sample data for user-book-link table
    user_book_links = [
        (1, 1),
        (1, 2),
    ]

    try:
        cursor = connection.cursor()
        for link in user_book_links:
            cursor.execute("INSERT INTO user_book_link (user_id, book_id) VALUES (%s, %s)", link)
        connection.commit()
        print("User-book-link table populated successfully!")
    except Error as e:
        print("Error inserting into user-book-link table:", e)

# Function to connect to MySQL with retry logic
def connect_to_mysql_with_retry():
    max_retries = 10
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        print(MYSQL_HOST)
        try:
            connection = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DB
            )
            if connection.is_connected():
                print("Connected to MySQL database")
                return connection
        except Error as e:
            print(e)
            print(f"Error connecting to MySQL (attempt {attempt+1}/{max_retries}): {e}")
            print("Retrying in {} seconds...".format(retry_delay))
            time.sleep(retry_delay)
    
    # If all retries fail, raise an exception
    raise Exception("Failed to connect to MySQL after {} attempts".format(max_retries))

# Main function
def main():
    connection = None
    try:
        # Connect to MySQL with retry logic
        connection = connect_to_mysql_with_retry()

        # Once connected, proceed with other database operations
        create_tables(connection)
        populate_user_table(connection)
        populate_book_table(connection)
        populate_user_book_link_table(connection)
    except Exception as e:
        print("Error:", e)
    finally:
        # Close the connection
        if connection and connection.is_connected():
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    main()