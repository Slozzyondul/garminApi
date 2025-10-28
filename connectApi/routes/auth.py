from flask import Blueprint, request, jsonify, session
from models.garmin_client import GarminClient
import os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login to Garmin Connect"""
    data = request.get_json()
    
    email = data.get('email') or os.environ.get('GARMIN_EMAIL')
    password = data.get('password') or os.environ.get('GARMIN_PASSWORD')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    try:
        client = GarminClient(email, password)
        
        if client.login():
            # Store client in session
            session['garmin_client'] = client
            session['logged_in'] = True
            session['email'] = email
            
            # Get user info
            user_info = client.get_user_summary()
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': user_info
            })
        else:
            return jsonify({'error': 'Login failed'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout from Garmin Connect"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@auth_bp.route('/status', methods=['GET'])
def status():
    """Check authentication status"""
    if 'logged_in' in session and session['logged_in']:
        return jsonify({
            'authenticated': True,
            'email': session.get('email')
        })
    else:
        return jsonify({'authenticated': False})