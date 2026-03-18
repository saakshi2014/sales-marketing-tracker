from flask import Flask, render_template
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(
    __name__,
    template_folder='../frontend/templates',
    static_folder='../frontend/static'
)

app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard/employee')
def employee_dashboard():
    return render_template('employee_dashboard.html')

@app.route('/dashboard/m1')
def m1_dashboard():
    return render_template('m1_dashboard.html')

@app.route('/dashboard/m2')
def m2_dashboard():
    return render_template('m2_dashboard.html')

# ── RUN ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)