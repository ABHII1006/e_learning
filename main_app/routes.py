from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.users_admin.services.user_service import UserService
from services.subjects.services.subject_service import SubjectService
import re
main_routes = Blueprint('main_routes', __name__, static_folder='static', template_folder='templates')

# Initialize services
user_service = UserService()
subject_service = SubjectService()

# Subjects list
subjects = ["math", "science", "history", "english"]
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PHONE_REGEX = r'^\d{10}$'
PASSWORD_REGEX = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$'
# Home page endpoint
@main_routes.route('/')
def index():
    return render_template('index.html')

# Admin Login endpoint
@main_routes.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        password = request.form['password']
        admin = user_service.admin_login(username_or_email, password)
        
        if admin is None or admin['password'] != password:
            flash('Invalid username or password', 'error')
            return render_template('admin_login.html')
        else:
            session['admin_id'] = admin['admin_id']
            session['role'] = 'admin'
            return redirect(url_for('main_routes.admin_dashboard'))
    else:
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
            # session['role'] = user['role']  # Get role from the database
            return redirect(url_for('main_routes.dashboard'))
    else:
        return render_template('login.html')

# Admin Dashboard endpoint
@main_routes.route('/admin_dashboard')
def admin_dashboard():
    if 'role' not in session or session['role'] != 'admin':
        flash('Access denied. Only admins can access this page.', 'error')
        return redirect(url_for('main_routes.dashboard'))
    return render_template('admin_dashboard.html', subjects=subjects)

# Post content endpoint
@main_routes.route('/post_content/<subject>', methods=['GET', 'POST'])
def post_content(subject):
    if request.method == 'POST':
        topic = request.form.get('topic')
        category = request.form.get('category')
        description = request.form.get('description')
        if subject_service.post_content(subject, topic, category, description):
            flash('Content posted successfully', 'success')
        else:
            flash('Failed to post content', 'error')
        return redirect(url_for('main_routes.admin_dashboard'))
    else:
        return render_template('post_content.html', subject=subject)

# Dashboard endpoint
@main_routes.route('/dashboard')
def dashboard():
    subject_data = subject_service.get_subjects()
    return render_template('dashboard.html', subjects=subjects, subject_data=subject_data)

@main_routes.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        # Validate email
        if not re.match(EMAIL_REGEX, email):
            flash('Invalid email format', 'error')
            return render_template('signup.html')

        # Validate phone number (10 digits only)
        if not re.match(PHONE_REGEX, phone):
            flash('Invalid phone number. It must be exactly 10 digits.', 'error')
            return render_template('signup.html')

        # Validate password (at least 6 chars, 1 letter, 1 number)
        if not re.match(PASSWORD_REGEX, password):
            flash('Password must be at least 6 characters long and include at least one letter and one number.',
                  'error')
            return render_template('signup.html')
        
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
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        # Validate email
        if not re.match(EMAIL_REGEX, email):
            flash('Invalid email format', 'error')
            return render_template('add_user.html')

        # Validate phone number (10 digits only)
        if not re.match(PHONE_REGEX, phone):
            flash('Invalid phone number. It must be exactly 10 digits.', 'error')
            return render_template('add_user.html')

        # Validate password (at least 6 chars, 1 letter, 1 number)
        if not re.match(PASSWORD_REGEX, password):
            flash('Password must be at least 6 characters long and include at least one letter and one number.',
                  'error')
            return render_template('add_user.html')

        if user_service.add_user(name, email, phone, password):
            flash('User created successfully', 'success')
            return redirect(url_for('main_routes.admin_dashboard'))
        else:
            flash('Email already exists', 'error')
    return render_template('add_user.html')

# Feature 2: Remove User
@main_routes.route('/remove_user', methods=['GET', 'POST'])
def remove_user():
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
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Validate email
        if not re.match(EMAIL_REGEX, email):
            flash('Invalid email format', 'error')
            return render_template('add_admin.html')

        # Validate password (at least 6 chars, 1 letter, 1 number)
        if not re.match(PASSWORD_REGEX, password):
            flash('Password must be at least 6 characters long and include at least one letter and one number.',
                  'error')
            return render_template('add_admin.html')

        if user_service.add_admin(username, email, password):
            flash('Admin added successfully', 'success')
            return redirect(url_for('main_routes.admin_dashboard'))
        else:
            flash('Email already exists', 'error')
    return render_template('add_admin.html')


# Feature 4: View Subjects
@main_routes.route('/view_subjects')
def view_subjects():
    if 'admin_id' not in session:
        flash('Access denied. Please log in as admin.', 'error')
        return redirect(url_for('main_routes.admin_login'))
    subject_data = subject_service.get_subjects()
    return render_template('view_subjects.html', subject_data=subject_data)

# Feature 5: Add Subject
@main_routes.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    if 'admin_id' not in session:
        flash('Access denied. Please log in as admin.', 'error')
        return redirect(url_for('main_routes.admin_login'))
    if request.method == 'POST':
        subject_name = request.form['subject_name']
        conn = subject_service.get_db_connection()
        try:
            conn.execute(f'''
                CREATE TABLE IF NOT EXISTS {subject_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL
                )
            ''')
            conn.commit()
            flash('Subject added successfully', 'success')
            return redirect(url_for('main_routes.admin_dashboard'))
        finally:
            conn.close()
    return render_template('add_subject.html')
