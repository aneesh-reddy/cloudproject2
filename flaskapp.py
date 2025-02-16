from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For flashing messages

DATABASE = 'users.db'

# Function to connect to the SQLite database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Allows column access by name
    return conn

# Function to create the users table if it doesn't exist
def create_users_table():
    with get_db_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users 
                        (username TEXT PRIMARY KEY, 
                         password TEXT, 
                         firstname TEXT, 
                         lastname TEXT, 
                         email TEXT)''')
        conn.commit()

# Route for the home page (register page)
@app.route('/')
def home():
    return render_template('register.html')

# Register new user
@app.route('/register', methods=['POST'])
def register_user():
    username = request.form['username']
    password = request.form['password']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']

    # Check if the username already exists
    with get_db_connection() as conn:
        existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if existing_user:
            flash('Username already taken, please choose another.')
            return redirect(url_for('home'))

        # Insert the new user into the database
        conn.execute("INSERT INTO users (username, password, firstname, lastname, email) VALUES (?, ?, ?, ?, ?)",
                     (username, password, firstname, lastname, email))
        conn.commit()

    return redirect(url_for('user_profile', username=username))

# View user profile page
@app.route('/profile/<username>')
def user_profile(username):
    with get_db_connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()

    if user:
        return render_template('profile.html', user=user)
    else:
        flash('User not found.')
        return redirect(url_for('home'))

# Login user
@app.route('/login', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with get_db_connection() as conn:
            user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()

        if user:
            return redirect(url_for('user_profile', username=username))
        else:
            flash('Invalid username or password!')
            return redirect(url_for('login_user'))

    return render_template('login.html')

if __name__ == '__main__':
    create_users_table()  # Ensure the table is created when the app starts
    app.run(host='0.0.0.0', port=80, debug=True)
