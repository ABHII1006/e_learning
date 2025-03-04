from services.subjects.utils.db_utils import get_db_connection
import sqlite3

class SubjectService:
    def get_db_connection(self):
        return get_db_connection()

    def post_content(self, subject, topic, category, description):
        conn = get_db_connection()
        try:
            # Check if the topic already exists in the subject table
            existing_topic = conn.execute(f'SELECT * FROM "{subject}" WHERE topic = ?', (topic,)).fetchone()

            with conn:
                if existing_topic:
                    # If the topic exists, update the existing row
                    conn.execute(f'UPDATE "{subject}" SET category = ?, description = ? WHERE topic = ?',
                                 (category, description, topic))
                    print(f"✅ Topic '{topic}' updated successfully in {subject}!")
                else:
                    # If the topic does not exist, insert a new row
                    conn.execute(f'INSERT INTO "{subject}" (topic, category, description) VALUES (?, ?, ?)',
                                 (topic, category, description))
                    print(f"✅ Topic '{topic}' added successfully in {subject}!")

            return True

        except sqlite3.Error as e:
            print(f"❌ Database error: {e}")
            return False

        finally:
            conn.close()

    def get_subjects(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Fetch table names (courses)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = cursor.fetchall()

            # Extract table names and ensure they are strings
            course_names = [table[0] for table in tables if table[0] is not None]
            print("Courses (Tables) in DB:", course_names)  # Debugging
            return course_names
        except sqlite3.Error as e:
            print("Database Error:", e)
            return []
        finally:
            conn.close()

    def create_subject(self, subject_name):
        conn = get_db_connection()
        try:
            with conn:
                conn.execute(f'''CREATE TABLE IF NOT EXISTS "{subject_name}" (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT UNIQUE NOT NULL,  -- Ensure topic is UNIQUE
                    category TEXT,
                    description TEXT
                )''')
            return True
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")
            return False
        finally:
            conn.close()

    # def delete_subject(self, course_name):
    #     conn = get_db_connection()
    #     cursor = conn.cursor()
    #
    #     try:
    #         # Drop the table if it exists
    #         cursor.execute(f"DROP TABLE IF EXISTS {course_name};")
    #         conn.commit()
    #         print(f"Deleted course (table): {course_name}")  # Debugging
    #         return True
    #     except sqlite3.Error as e:
    #         print("Database Error:", e)
    #         return False
    #     finally:
    #         conn.close()


    def delete_topic_or_course(self,course_name, topic_name):
        """Handles deleting a specific topic, all topics, or an entire course."""
        if not course_name:
            return False, "Invalid request. No course specified."

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            if topic_name == "all_course":
                # Drop the entire table (delete course)
                cursor.execute(f"DROP TABLE IF EXISTS {course_name};")
                message = f'Entire course "{course_name}" deleted successfully!'
            elif topic_name.lower() == "all topics":
                # Delete all rows but keep the table
                cursor.execute(f"DELETE FROM {course_name};")
                message = f'All topics from "{course_name}" removed successfully!'
            else:
                # Delete only the selected topic (row)
                cursor.execute(f"DELETE FROM {course_name} WHERE topic = ?;", (topic_name,))
                message = f'Topic "{topic_name}" removed from "{course_name}".'

            conn.commit()
            return True, message

        except sqlite3.Error as e:
            return False, f"Database error: {e}"

        finally:
            conn.close()

    def get_topics_from_db(self, course_name):
        """Fetch all topics from a course. If no topics exist, return only 'all' to delete the entire course."""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(f"SELECT DISTINCT topic FROM {course_name};")
            topics = [row[0] for row in cursor.fetchall()]

            if not topics:
                return ["All Topics"]  # If no topics exist, only allow deleting the whole course

            topics.insert(0, "All Topics")  # Add "All" option at the top
            return topics
        except sqlite3.Error as e:
            print("Database Error:", e)
            return []
        finally:
            conn.close()

    def get_topics_by_course(self,course):
        """Fetches topics (id, topic, description) from the given course."""
        try:
            conn = subject_service.get_db_connection()  # Get DB connection
            query = f'SELECT id, topic, description FROM "{course}"'
            topics = conn.execute(query).fetchall()
            conn.close()

            return topics, None  # Return topics and no error

        except sqlite3.OperationalError as e:
            return None, f"Error fetching topics: {e}"  # Return error message

    def get_topic_details_from_db(self,course_name, topic_id):
        """Fetches category and description for a given topic in a course."""
        try:
            conn = subject_service.get_db_connection()  # Get DB connection
            query = f'SELECT category, description FROM "{course_name}" WHERE id = ?'
            topic = conn.execute(query, (topic_id,)).fetchone()
            conn.close()

            return topic, None  # Return topic details and no error

        except sqlite3.Error as e:
            return None, str(e)  # Return error message

    def add_subject_to_db(subject_name):
        """Creates a new subject (table) in the database."""
        conn = subject_service.get_db_connection()
        try:
            query = f'''
                CREATE TABLE IF NOT EXISTS "{subject_name}" (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL
                )
            '''
            conn.execute(query)
            conn.close()
            return True, None  # ✅ Success, No error
        except sqlite3.Error as e:
            return False, str(e)  # ❌ Failure, Return error


subject_service = SubjectService()
