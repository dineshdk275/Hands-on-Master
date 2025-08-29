
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask import Flask, send_from_directory
import datetime
import os
from flask_sqlalchemy import SQLAlchemy

# --- App & DB setup ---

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # For flash messages

# Database config: uses DATABASE_URL (postgres) if provided, else falls back to SQLite for local dev
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    # SQLAlchemy expects postgresql://
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL or 'sqlite:///local.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# --- Models ---
class LearningPath(db.Model):
    __tablename__ = 'learning_paths'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    level = db.Column(db.String(50), nullable=True)  # e.g., Beginner, Intermediate, Advanced
    duration_hours = db.Column(db.Integer, nullable=True)


class Challenge(db.Model):
    __tablename__ = 'challenges'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.String(50), nullable=True)  # e.g., Easy, Medium, Hard
    points = db.Column(db.Integer, default=0)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=True)
    points = db.Column(db.Integer, default=0)

# Add request logging
@app.before_request
def log_request():
    print(f"[{datetime.datetime.now()}] {request.method} {request.url}")
    print(f"User-Agent: {request.headers.get('User-Agent', 'N/A')}")

# Static credentials
VALID_CREDENTIALS = {
    'username': 'codecrafters',
    'email': 'codecub@gmail.com',
    'password': 'codecrafters'
}

@app.route('/')
def home():
    return render_template('landing_page.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    print(f"Login route accessed with method: {request.method}")  # Debug
    if request.method == 'POST':
        print("POST request received")  # Debug
        print(f"Form data: {request.form}")  # Debug
        
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        print(f"Login attempt - Username: '{username}', Password: '{password}'")  # Debug
        print(f"Expected - Username: '{VALID_CREDENTIALS['username']}', Password: '{VALID_CREDENTIALS['password']}'")  # Debug
        
        # Check static credentials
        if username == VALID_CREDENTIALS['username'] and password == VALID_CREDENTIALS['password']:
            print("Login successful, redirecting to dashboard")  # Debug
            return redirect(url_for('dashboard'))
        else:
            print("Login failed")  # Debug
            flash('Invalid username or password! Use: codecrafters / codecrafters', 'error')
            return render_template('login.html', mode='login')
    
    print("GET request, rendering login page")  # Debug
    # Check if we should show login mode (after registration)
    mode = request.args.get('mode', 'register')
    print(f"Rendering login page with mode: {mode}")  # Debug
    return render_template('login.html', mode=mode)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '')
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        
        print(f"Registration attempt - Username: {username}, Email: {email}, Password: {password}")  # Debug
        
        # Check if credentials match our static ones for registration
        if (username == VALID_CREDENTIALS['username'] and 
            email == VALID_CREDENTIALS['email'] and 
            password == VALID_CREDENTIALS['password']):
            print("Registration successful")  # Debug
            flash('Registration successful! Please login with your credentials.', 'success')
            # Redirect to login with a parameter to switch to login mode
            return redirect(url_for('login') + '?mode=login')
        else:
            print("Registration failed")  # Debug
            flash('Registration failed! Use: codecrafters / codecub@gmail.com / codecrafters', 'error')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    print("Dashboard route accessed!")  # Debug
    return render_template('dashboard.html')


# --- Learning Paths ---
@app.route('/learning-paths')
def learning_paths():
    try:
        items = LearningPath.query.order_by(LearningPath.id.desc()).all()
    except Exception as e:
        print(f"Error fetching learning paths: {e}")
        items = []
    return render_template('learning_paths.html', items=items)


@app.route('/api/learning-paths')
def api_learning_paths():
    try:
        items = LearningPath.query.order_by(LearningPath.id.desc()).all()
        data = [
            {
                'id': i.id,
                'title': i.title,
                'description': i.description,
                'level': i.level,
                'duration_hours': i.duration_hours,
            }
            for i in items
        ]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- Challenges ---
@app.route('/challenges')
def challenges():
    try:
        items = Challenge.query.order_by(Challenge.id.desc()).all()
    except Exception as e:
        print(f"Error fetching challenges: {e}")
        items = []
    return render_template('challenges.html', items=items)


@app.route('/api/challenges')
def api_challenges():
    try:
        items = Challenge.query.order_by(Challenge.id.desc()).all()
        data = [
            {
                'id': i.id,
                'title': i.title,
                'description': i.description,
                'difficulty': i.difficulty,
                'points': i.points,
            }
            for i in items
        ]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- Leaderboard ---
@app.route('/leaderboard')
def leaderboard():
    try:
        # Ensure ordering by 'points' column
        users = User.query.order_by(User.points.desc()).limit(20).all()
    except Exception as e:
        print(f"Error fetching leaderboard: {e}")
        users = []
    return render_template('leaderboard.html', users=users)


@app.route('/api/leaderboard')
def api_leaderboard():
    try:
        users = User.query.order_by(User.points.desc()).limit(20).all()
        data = [
            {
                'id': u.id,
                'name': u.name,
                'points': u.points,
            }
            for u in users
        ]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- AI Tutor (placeholder) ---
@app.route('/ai-tutor')
def ai_tutor():
    return render_template('ai_tutor.html')

@app.route('/test')
def test():
    return "Test route working! Dashboard should work too."

@app.route('/who-we-are')
def who_we_are():
    return render_template('who_we_are.html')


if __name__ == '__main__':
    # Create tables if they don't exist (safe for local dev)
    try:
        with app.app_context():
            db.create_all()
    except Exception as e:
        print(f"DB init error: {e}")
    app.run(debug=True, port=5001)
