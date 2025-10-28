from flask import Flask, render_template, session
from flask_cors import CORS
from flask_session import Session
from datetime import timedelta
import os
from dotenv import load_dotenv

from utils.data_analyzer import DataAnalyzer
from routes.api import api_bp
from routes.auth import auth_bp

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize extensions
CORS(app)
Session(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Main dashboard"""
    if 'logged_in' not in session:
        return render_template('index.html', error='Please login first')
    return render_template('dashboard.html')

@app.route('/activities')
def activities():
    """Activities page"""
    if 'logged_in' not in session or 'garmin_client' not in session:
        return render_template('index.html', error='Please login first')

    client = session.get('garmin_client')
    try:
        # Ensure client is logged in before making a request
        if not client.client:
            if not client.login():
                session.clear()
                return render_template('index.html', error='Session expired. Please login again.')

        activity_list = client.get_activities(limit=50)  # Fetch up to 50 recent activities

        # Use the same analyzer as the API for consistency
        analyzer = DataAnalyzer()
        enriched_activities = analyzer.enrich_activities(activity_list) if activity_list else []

        return render_template('activities.html', activities=enriched_activities)
    except Exception as e:
        return render_template('activities.html', error=f"Could not fetch activities: {e}")

@app.route('/devices')
def devices():
    """Device information page"""
    if 'logged_in' not in session or 'garmin_client' not in session:
        return render_template('index.html', error='Please login first')

    client = session.get('garmin_client')
    try:
        if not client.client:
            if not client.login():
                session.clear()
                return render_template('index.html', error='Session expired. Please login again.')

        device_list = client.get_devices()
        return render_template('device_info.html', devices=device_list)
    except Exception as e:
        return render_template('device_info.html', error=f"Could not fetch devices: {e}")

@app.errorhandler(404)
def not_found(error):
    return render_template('base.html', error='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html', error='Internal server error'), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)