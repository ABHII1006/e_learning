from services.users_admin.utils.db_utils import get_db_connection
import bcrypt
import sqlite3
from flask import session

class UserService:
    def get_db_connection(self):
        return get_db_connection()
    
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password, hashed_password):
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def login(self, email, password):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
        conn.close()
        return user

    def signup(self, name, email, phone, password):
        conn = get_db_connection()
        existing_user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if existing_user is None:
            conn.execute('INSERT INTO users (name, email, phone, password) VALUES (?, ?, ?, ?)', (name, email, phone, password))
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False

    def admin_login(self, username_or_email, password):
        conn = get_db_connection()
        admin = conn.execute('SELECT * FROM admins WHERE email = ? AND password = ?', (username_or_email, password)).fetchone()
        conn.close()
        return admin

    # Add User
    def add_user(self, name, email, phone, password):
        conn = get_db_connection()
        try:
            existing_user = conn.execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            ).fetchone()
            print("Existing User:", existing_user)  # Debugging print

            if existing_user is None:
                conn.execute(
                    "INSERT INTO users (name, email, phone, password) VALUES (?, ?, ?, ?)",
                    (name, email, phone, password),
                )
                conn.commit()
                print("User Added:", name, email)  # Debugging print
                return True
            else:
                print("User already exists!")
                return False

        except sqlite3.Error as e:
            print("DB Error:", e)
            return False

        finally:
            if conn:
                conn.close()  # ✅ Ensures connection closes even after an error


    # Remove User
    def remove_user(self, email):
        conn = get_db_connection()
        try:
            existing_user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
            if existing_user is not None:
                conn.execute('DELETE FROM users WHERE email = ?', (email,))
                conn.commit()
                conn.close()
                return True
            else:
                conn.close()
                return False
        except sqlite3.Error as e:
            conn.close()
            return False

    # Add Admin
    def add_admin(self, username, email, password):
        conn = get_db_connection()
        try:
            existing_admin = conn.execute('SELECT * FROM admins WHERE email = ?', (email,)).fetchone()
            if existing_admin is None:
                conn.execute('INSERT INTO admins (username, email, password) VALUES (?, ?, ?)',
                             (username, email, password))
                conn.commit()
                conn.close()
                return True
            else:
                conn.close()
                return False
        except sqlite3.Error as e:
            conn.close()
            return False
        
     #admin_details   
    def get_admin_details():
        admin_id = session.get("admin_id")  # Ensure admin is logged in
        if not admin_id:
            return ("Admin", "Admin")  # Default if session expired
        
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, role FROM admins WHERE id = ?", (admin_id,))
        admin = cursor.fetchone()
        conn.close()
        
        return admin if admin else ("Admin", "Admin")
    
    #user_dash
    def get_user_by_id(self,user_id):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            return {'id': user[0], 'name': user[1]}
        return None

    def get_user_details(self,user_id):
        """Fetches user details (name, courses) from the database."""
        try:
            conn = get_db_connection()  # Get the database connection
            user = conn.execute('SELECT name, courses FROM users WHERE id = ?', (user_id,)).fetchone()
            conn.close()

            if user:
                courses = user['courses'].split(',') if user['courses'] else []
                return user, courses, None  # Return user details and courses list

            return None, None, "User not found in database!"

        except Exception as e:
            return None, None, str(e)  # Return error message

