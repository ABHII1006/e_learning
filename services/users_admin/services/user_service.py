from services.users_admin.utils.db_utils import get_db_connection
import sqlite3

class UserService:
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
        admin = conn.execute('SELECT * FROM admins WHERE username = ? OR email = ?', (username_or_email, username_or_email)).fetchone()
        conn.close()
        return admin

    # Add User
    def add_user(self, name, email, phone, password):
        conn = get_db_connection()
        try:
            existing_user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
            if existing_user is None:
                conn.execute('INSERT INTO users (name, email, phone, password) VALUES (?, ?, ?, ?)',
                             (name, email, phone, password))
                conn.commit()
                conn.close()
                return True
            else:
                conn.close()
                return False
        except sqlite3.Error as e:
            conn.close()
            return False

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
