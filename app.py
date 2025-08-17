from flask import Flask, render_template, request, redirect, url_for, flash
from flask import Flask, send_from_directory
import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # For flash messages

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

@app.route('/About.html')
def about():
    return send_from_directory('templates', 'About.html')

@app.route('/test')
def test():
    return "Test route working! Dashboard should work too."

if __name__ == '__main__':
    app.run(debug=True, port=5001)
