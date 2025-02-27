from ..utils.db_utils import get_db_connection
import sqlite3

class SubjectService:
    def post_content(self, subject, topic, category, description):
        conn = get_db_connection()
        try:
            conn.execute(f'INSERT INTO {subject} (topic, category, description) VALUES (?, ?, ?)', (topic, category, description))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            conn.close()
            return False

    def get_subjects(self):
        conn = get_db_connection()
        subjects = ["math", "science", "history", "english"]
        subject_data = {}
        for subject in subjects:
            rows = conn.execute(f'SELECT * FROM {subject}').fetchall()
            subject_data[subject] = rows
        conn.close()
        return subject_data
