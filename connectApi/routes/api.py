from flask import Blueprint, jsonify, request, session, send_file
from models.garmin_client import GarminClient
from utils.fit_parser import FitParser
from utils.data_analyzer import DataAnalyzer
import io
import json
from datetime import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/activities', methods=['GET'])
def get_activities():
    """Get user activities"""
    if 'garmin_client' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    limit = request.args.get('limit', 20, type=int)
    start = request.args.get('start', 0, type=int)
    
    try:
        client = session.get('garmin_client')
        activities = client.get_activities(limit, start)
        
        if activities:
            # Process and enrich activity data
            analyzer = DataAnalyzer()
            enriched = analyzer.enrich_activities(activities)
            return jsonify({
                'success': True,
                'data': enriched,
                'count': len(enriched)
            })
        else:
            return jsonify({'error': 'No activities found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/activity/<activity_id>', methods=['GET'])
def get_activity_detail(activity_id):
    """Get detailed activity information"""
    if 'garmin_client' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        client = session.get('garmin_client')
        activity = client.get_activity_details(activity_id)
        
        if activity:
            return jsonify({
                'success': True,
                'data': activity
            })
        else:
            return jsonify({'error': 'Activity not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/activity/<activity_id>/download', methods=['GET'])
def download_activity(activity_id):
    """Download activity file"""
    if 'garmin_client' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    format = request.args.get('format', 'FIT').upper()
    
    try:
        client = session.get('garmin_client')
        data = client.download_activity(activity_id, format)
        
        if data:
            return send_file(
                io.BytesIO(data),
                mimetype='application/octet-stream',
                as_attachment=True,
                download_name=f'activity_{activity_id}.{format.lower()}'
            )
        else:
            return jsonify({'error': 'Download failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/devices', methods=['GET'])
def get_devices():
    """Get user devices"""
    if 'garmin_client' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        client = session.get('garmin_client')
        devices = client.get_devices()
        
        if devices:
            return jsonify({
                'success': True,
                'data': devices,
                'count': len(devices)
            })
        else:
            return jsonify({'error': 'No devices found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/heart-rate', methods=['GET'])
def get_heart_rate():
    """Get heart rate data"""
    if 'garmin_client' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        client = session.get('garmin_client')
        hr_data = client.get_heart_rate_data(date)
        
        if hr_data:
            # Analyze heart rate data
            analyzer = DataAnalyzer()
            analysis = analyzer.analyze_heart_rate(hr_data)
            
            return jsonify({
                'success': True,
                'data': hr_data,
                'analysis': analysis
            })
        else:
            return jsonify({'error': 'No heart rate data found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/sleep', methods=['GET'])
def get_sleep():
    """Get sleep data"""
    if 'garmin_client' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        client = session.get('garmin_client')
        sleep_data = client.get_sleep_data(date)
        
        if sleep_data:
            return jsonify({
                'success': True,
                'data': sleep_data
            })
        else:
            return jsonify({'error': 'No sleep data found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/stress', methods=['GET'])
def get_stress():
    """Get stress data"""
    if 'garmin_client' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        client = session.get('garmin_client')
        stress_data = client.get_stress_data(date)
        
        if stress_data:
            return jsonify({
                'success': True,
                'data': stress_data
            })
        else:
            return jsonify({'error': 'No stress data found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/stats/summary', methods=['GET'])
def get_stats_summary():
    """Get overall statistics summary"""
    if 'garmin_client' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        client = session.get('garmin_client')
        summary = client.get_user_summary()
        
        if summary:
            return jsonify({
                'success': True,
                'data': summary
            })
        else:
            return jsonify({'error': 'No summary data found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/upload/fit', methods=['POST'])
def upload_fit_file():
    """Upload and parse FIT file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename.endswith('.fit'):
        try:
            # Parse FIT file
            parser = FitParser()
            data = parser.parse_fit_file(file)
            
            # Analyze parsed data
            analyzer = DataAnalyzer()
            analysis = analyzer.analyze_fit_data(data)
            
            return jsonify({
                'success': True,
                'data': data,
                'analysis': analysis
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Invalid file format'}), 400