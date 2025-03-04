import sqlite3

def create_tables():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Users table with role
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            courses TEXT
            
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Insert admin user if table is empty
    cursor.execute('SELECT * FROM admins')
    if not cursor.fetchone():
        cursor.execute('INSERT INTO admins (username,email, password) VALUES (?,?, ?)', ('admin','admin@gmail.com' ,'password123'))

    conn.commit()
    conn.close()


# Define get_db_connection function
def get_db_connection():
    conn = sqlite3.connect('users.db', timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


# Call the function to create tables
create_tables()
