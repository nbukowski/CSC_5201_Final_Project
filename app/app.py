import time
from flask import Flask, redirect, request, jsonify, render_template, session, url_for
import mysql.connector
from mysql.connector import Error
from auth import Auth
from functools import wraps
from prometheus_client import Counter, Histogram
from prometheus_client.exposition import generate_latest



app = Flask(__name__)
REQUEST_COUNT = Counter('request_count', 'App Request Count', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('request_latency_ms', 'Request latency in milliseconds', ['method', 'endpoint'])


app.secret_key = 'your_secret_key_here' 
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

# MySQL connection configuration
MYSQL_HOST = 'mysql'
MYSQL_USER = 'myuser'
MYSQL_PASSWORD = 'mypassword'
MYSQL_DB = 'mydatabase'

# JWT secret key
JWT_SECRET_KEY = 'your_secret_key_here'

# Initialize Auth class
auth = Auth(JWT_SECRET_KEY)

def token_required(f):
    # Function to authenticate JWT token
    @wraps(f)
    def decorated(*args, **kwargs):
        
        token = session.get('jwtToken')

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        payload = auth.verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401

        return f(payload, *args, **kwargs)
    return decorated

def connect_to_mysql():
    # Function to connect to MySQL
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
        print("Error connecting to MySQL:", e)

def get_books(user_id=None):
    try:
        connection = connect_to_mysql()
        cursor = connection.cursor(dictionary=True)
        if user_id:
            query = "SELECT book.id, book.title, book.author, book.isbn, book.coverimage FROM book INNER JOIN user_book_link ON book.id = user_book_link.book_id WHERE user_book_link.user_id = %s"
            cursor.execute(query,(user_id,))
        # No filtering == fetch all books
        else:
            query = "SELECT book.id, book.title, book.author, book.isbn, book.coverimage FROM book"
            cursor.execute(query)
        books = cursor.fetchall()
        connection.close()
        # Returns books as a list of dictionaries
        return books
    except Error as e:
        print("Error querying database:", e)
        return jsonify({'error': str(e)}), 500

# Public Catalog Route
@app.route('/public_catalog')
@token_required
def public_catalog(payload):
    books = get_books()
    return render_template('public_catalog.html', books=books)

# Users personal Catalog Route
@app.route('/my_catalog')
@token_required
def my_catalog(payload):
    books = get_books(payload.get('user_id'))
    return render_template('user_catalog.html', books=books)

# Check out book route from public library page
@app.route('/books/checkout/<int:book_id>', methods=['POST'])
@token_required
def checkout_book(payload, book_id):
    try:
        user_id = payload.get('user_id')

        connection = connect_to_mysql()
        cursor = connection.cursor()
        query = "INSERT INTO user_book_link (book_id, user_id) VALUES (%s, %s)"
        cursor.execute(query, (book_id, user_id))
        connection.commit()
        connection.close()
        
        return jsonify({'message': 'Book checked out successfully'}), 201
    except Error as e:
        print("Error during book checkout:", e)
        return jsonify({'error': 'Failed to check out book'}), 500
    
# Allow user to drop book from library
@app.route('/books/drop/<int:book_id>', methods=['POST'])
@token_required
def drop_book(payload, book_id):
    try:
        user_id = payload.get('user_id')

        connection = connect_to_mysql()
        cursor = connection.cursor()
        query = "DELETE FROM user_book_link WHERE book_id = %s AND user_id = %s"
        cursor.execute(query, (book_id, user_id))
        connection.commit()
        connection.close()

        return jsonify({'message': 'Book dropped from library'}), 201
    except Error as e:
        print("Error during book drop:", e)
        return jsonify({'error': 'Failed to drop book'}), 500

# Login route
@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        connection = None
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            # Checks if user exists in database
            connection = connect_to_mysql()
            cursor = connection.cursor()
            query = "SELECT id FROM user WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            user_id = cursor.fetchone()

            if user_id:
                # User exists, generates JWT token
                token = auth.create_token(user_id[0])
                session['jwtToken'] = token
                return redirect(url_for('my_catalog'))
            else:
                return jsonify({'error': 'Invalid username or password'}), 401
        except Exception as e:
            print("Error during login:", e)
            return jsonify({'error': str(e)}), 500
        finally:
            if connection:
                connection.close()
    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    # Deletes 'jwtToken' session variable
    session.pop('jwtToken', None)
    return render_template('login.html')

# Metrics Route for promethetus to access
@app.route('/metrics')
# Function defines route to Flask app for Prometheus to query and collect metrics. 
def metrics():
    return generate_latest()

@app.before_request
def before_request():
    # Function execited before each request to Flask application. Used to record the start time of request in milliseconds. 
    # Will be used for calculating latency of requests
    request.start_time = round(time.time() * 1000) # records current time in milliseconds (*1000 conversion to go from seconds to milliseconds)

@app.after_request
# Function executed after Flask request. Also aids in calculating latency request & updates Prometheus metrics
def after_request(response):
    request_latency = round(time.time() * 1000) - request.start_time # calculate latency
    REQUEST_COUNT.labels(request.method, request.path).inc() # increments count metric for total number of requests ( labeled by HTTP and request path)
    REQUEST_LATENCY.labels(request.method, request.path).observe(request_latency) # observes latency request
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

