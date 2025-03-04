import sqlite3

def create_tables():
    conn = sqlite3.connect('subjects.db')
    cursor = conn.cursor()

    # Subject tables
    subjects = ["math", "science", "history", "english"]
    for subject in subjects:
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {subject} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL
            )
        ''')


    conn.commit()
    conn.close()


# Define get_db_connection function
def get_db_connection():
    conn = sqlite3.connect('subjects.db')
    conn.row_factory = sqlite3.Row
    return conn


# Call the function to create tables
create_tables()
