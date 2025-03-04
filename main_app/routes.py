from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from services.users_admin.services.user_service import UserService
from services.subjects.services.subject_service import SubjectService
import sqlite3

main_routes = Blueprint('main_routes', __name__, static_folder='static', template_folder='templates')

# Initialize services
user_service = UserService()
subject_service = SubjectService()

# Subjects list
# subjects = ["math", "science", "history", "english"]

# Home page endpoint
@main_routes.route('/')
def index():
    return render_template('index.html')

# Admin Login endpoint
@main_routes.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        identifier = request.form['identifier']  # Can be email, username, or phone
        password = request.form['password']

        admin = user_service.admin_login(identifier, password)

        if admin is None:
            flash('Invalid credentials', 'error')
            return render_template('admin_login.html')

        # Store admin details in session
        session['admin_id'] = admin['admin_id']
        session['admin_name'] = admin['username']
        session['admin_email'] = admin['email']
        session['role'] = 'admin'

        return redirect(url_for('main_routes.admin_dashboard'))
    
    return render_template('admin_login.html')


# User Login endpoint
@main_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = user_service.login(email, password)

        if user is None:
            flash('Invalid email or password', 'error')
            return render_template('login.html')
        else:
            session['user_id'] = user['id']
            # session['role'] = 'user'  # Setting User Role
            return redirect(url_for('main_routes.dashboard'))
    else:
        return render_template('login.html')

# Admin Dashboard endpoint
@main_routes.route('/admin_dashboard')
def admin_dashboard():
    # Ensure only admins can access the dashboard
    if 'role' not in session or session['role'] != 'admin':
        flash('Access denied. Please log in as admin.', 'error')
        return redirect(url_for('main_routes.login'))

    # Fetch all users from the database
    conn = user_service.get_db_connection()
    users = conn.execute('SELECT id, name AS username, email, phone, courses FROM users').fetchall()
    conn.close()

    # Fetch course names from subjects.db
    course_names = subject_service.get_subjects()  # Fetch table names dynamically

    # Get the current logged-in admin's name
    admin_name = session.get('admin_name', 'Admin')

    return render_template('admin_dashboard.html', admin_name=admin_name, users=users, course_names=course_names)

# User dashboard endpoint
# User dashboard endpoint
@main_routes.route('/dashboard')
def dashboard():
    """API route to load the dashboard for a logged-in user."""
    if 'user_id' not in session:
        flash('Access denied. Please log in.', 'error')
        return redirect(url_for('main_routes.login'))

    user_id = session['user_id']  # Get logged-in user ID
    user, courses, error =user_service.get_user_details(user_id)

    if error:
        flash(error, "error")
        return redirect(url_for('main_routes.login'))

    return render_template('dashboard.html', user=user, courses=courses)


@main_routes.route('/topics/<course>')
def topics(course):
    """API route to fetch topics for a given course."""
    topics, error = subject_service.get_topics_by_course(course)  # ✅ Calls function

    if error:
        flash(error, "error")
        return redirect(url_for('main_routes.dashboard'))

    return render_template('topics.html', course=course, topics=topics)


# 📌 API to Fetch Topic Details (Category & Description)
@main_routes.route('/get_topic_details/<course_name>/<int:topic_id>')
def get_topic_details(course_name, topic_id):
    """API route to fetch topic details (category & description)."""
    topic, error = subject_service.get_topic_details_from_db(course_name, topic_id)  # ✅ Calls function

    if error:
        return jsonify({'error': error}), 500

    if topic:
        return jsonify({'category': topic['category'], 'description': topic['description']})

    return jsonify({'error': 'Topic not found'}), 404




# Add Subject endpoint
@main_routes.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    """API route to add a new subject (table)."""
    if 'role' not in session or session['role'] != 'admin':
        flash('Access denied. Please log in as admin.', 'error')
        return redirect(url_for('main_routes.admin_login'))

    if request.method == 'POST':
        subject_name = request.form['subject_name'].strip()

        if not subject_name:
            flash('Subject name cannot be empty.', 'error')
            return redirect(url_for('main_routes.add_subject'))

        success, error = subject_service.add_subject_to_db(subject_name)  # ✅ Calls function

        if success:
            flash('Subject added successfully', 'success')
        else:
            flash(f'Error adding subject: {error}', 'error')

        return redirect(url_for('main_routes.admin_dashboard'))

    return render_template('add_subject.html')





@main_routes.route('/post_content', methods=['GET', 'POST'])
def post_content():
    courses = subject_service.get_subjects()

    if request.method == 'POST':
        course = request.form.get('updateCourse')
        topic = request.form.get('topic')
        category = request.form.get('category')
        description = request.form.get('description')

        if not course:
            flash('Please select a course.', 'error')
            return redirect(url_for('main_routes.post_content'))  # ✅ Fixed

        if subject_service.post_content(course, topic, category, description):
            flash(f'Content posted for {course}!', 'success')
        else:
            flash(f'Error posting content for {course}.', 'error')

        return redirect(url_for('main_routes.post_content'))  # ✅ Fixed

    return render_template('post_content.html', courses=courses)


from flask import flash, redirect, url_for, render_template

@main_routes.route('/add_course', methods=['POST'])
def add_course():
    new_course = request.form.get('new_course').strip().lower()

    if not new_course:
        flash("⚠️ Course name cannot be empty!", "warning")
        return redirect(url_for('main_routes.post_content'))  # Redirect back to post_content

    # Check if the course already exists
    existing_courses = subject_service.get_subjects()  # Fetch existing courses
    if new_course in existing_courses:
        flash(f"⚠️ Course '{new_course}' already exists!", "warning")
        return redirect(url_for('main_routes.post_content'))

    # Try creating the course
    success = subject_service.create_subject(new_course)
    if success:
        flash(f"✅ Course '{new_course}' created successfully!", "success")
    else:
        flash(f"❌ Error creating course '{new_course}'.", "danger")

    return redirect(url_for('main_routes.post_content'))

@main_routes.route('/remove_course', methods=['POST'])
def remove_course():
    """API endpoint to remove a topic or an entire course."""
    data = request.get_json()
    course_name = data.get('course')
    topic_name = data.get('topic')

    success, message = subject_service.delete_topic_or_course(course_name, topic_name)

    if success:
        flash(f"✅ {message}", "success")
        return jsonify({"message": message}), 200
    else:
        flash(f"❌ {message}", "danger")
        return jsonify({"message": message}), 400


@main_routes.route('/get_topics', methods=['GET'])
def get_topics():
    course_name = request.args.get('course')

    if not course_name:
        return jsonify({"topics": []})

    topics = subject_service.get_topics_from_db(course_name)
    return jsonify({"topics": topics})



# # Dashboard endpoint
# @main_routes.route('/dashboard')
# def dashboard():
#     subject_data = subject_service.get_subjects()
#     return render_template('dashboard.html', subjects=subjects, subject_data=subject_data)

@main_routes.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        
        if user_service.signup(name, email, phone, password):
            flash('User created successfully', 'success')
            return redirect(url_for('main_routes.login'))
        else:
            flash('Email already exists', 'error')
    return render_template('signup.html')

# Feature 1: Add User
@main_routes.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')

        if user_service.add_user(name, email, phone, password):  # CALL FUNCTION
            flash(f"User {name} added successfully!", "success")
            return redirect(url_for('main_routes.admin_dashboard'))
        else:
            flash("Error: Email already exists or DB error!", "error")
            return redirect(url_for('main_routes.add_user'))  # Fix redirect

    return render_template('add_user.html')


# Feature 2: Remove User
@main_routes.route('/remove_user', methods=['GET', 'POST'])
def remove_user():
    if 'role' not in session or session['role'] != 'admin':
        flash('Access denied. Only admins can access this page.', 'error')
        return redirect(url_for('main_routes.admin_login'))
    if request.method == 'POST':
        email = request.form['email']

        if user_service.remove_user(email):
            flash('User removed successfully', 'success')
            return redirect(url_for('main_routes.admin_dashboard'))
        else:
            flash('User not found', 'error')
    return render_template('remove_user.html')

# Feature 3: Add Admin
@main_routes.route('/add_admin', methods=['GET', 'POST'])
def add_admin():
    if 'role' not in session or session['role'] != 'admin':
        flash('Access denied. Only admins can access this page.', 'error')
        return redirect(url_for('main_routes.admin_login'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if user_service.add_admin(username, email, password):
            flash('Admin added successfully', 'success')
            return redirect(url_for('main_routes.admin_dashboard'))
        else:
            flash('Email already exists', 'error')
    return render_template('add_admin.html')

# Feature 4: View Subjects
@main_routes.route('/view_subjects')
def view_subjects():
    if 'role' not in session or session['role'] != 'admin':
        flash('Access denied. Please log in as admin.', 'error')
        return redirect(url_for('main_routes.admin_login'))
    subject_data = subject_service.get_subjects()  # Fetch subjects dynamically
    return render_template('view_subjects.html', subject_data=subject_data)

@main_routes.route('/logout')
def logout():
    session.clear()  # Clears all session data
    flash("You have been logged out.", "success")

    # Determine redirection based on user type
    user_type = request.args.get('user_type')

    if user_type == 'admin':
        return redirect(url_for('main_routes.admin_login'))  # Redirect to admin login
    else:
        return redirect(url_for('main_routes.login'))  # Redirect to regular login

@main_routes.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


