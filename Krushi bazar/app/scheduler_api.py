 # Scheduler API endpoints
from flask import Blueprint, jsonify, request
from datetime import datetime
from app.scheduler import scheduler

scheduler_bp = Blueprint('scheduler', __name__, url_prefix='/scheduler')

@scheduler_bp.route('/start', methods=['POST'])
def start_scheduler():
    """
    Start the automated scraping scheduler
    """
    try:
        success = scheduler.start_scheduler()
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Scheduler started successfully',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to start scheduler',
                'timestamp': datetime.now().isoformat()
            }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error starting scheduler: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@scheduler_bp.route('/stop', methods=['POST'])
def stop_scheduler():
    """
    Stop the automated scraping scheduler
    """
    try:
        success = scheduler.stop_scheduler()
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Scheduler stopped successfully',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to stop scheduler',
                'timestamp': datetime.now().isoformat()
            }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error stopping scheduler: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@scheduler_bp.route('/status', methods=['GET'])
def get_scheduler_status():
    """
    Get current scheduler status
    """
    try:
        status = scheduler.get_scheduler_status()
        return jsonify({
            'status': 'success',
            'data': status,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error getting scheduler status: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@scheduler_bp.route('/run-now', methods=['POST'])
def run_scheduler_now():
    """
    Run scheduled scraping immediately
    """
    try:
        scheduler.run_now()
        return jsonify({
            'status': 'success',
            'message': 'Scheduled scraping started immediately',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error running scheduled scraping: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@scheduler_bp.route('/add-state', methods=['POST'])
def add_state_to_schedule():
    """
    Add a state to the scheduled scraping list
    """
    try:
        data = request.get_json()
        if not data or 'state_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'state_id is required',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        state_id = data['state_id']
        success = scheduler.add_state_to_schedule(state_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'State ID {state_id} added to schedule. The system will automatically scrape all districts for this state.',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': f'State ID {state_id} already in schedule or invalid',
                'timestamp': datetime.now().isoformat()
            }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error adding state to schedule: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@scheduler_bp.route('/remove-state', methods=['POST'])
def remove_state_from_schedule():
    """
    Remove a state from the scheduled scraping list
    """
    try:
        data = request.get_json()
        if not data or 'state_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'state_id is required',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        state_id = data['state_id']
        success = scheduler.remove_state_from_schedule(state_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'State ID {state_id} removed from schedule',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': f'State ID {state_id} not found in schedule',
                'timestamp': datetime.now().isoformat()
            }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error removing state from schedule: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@scheduler_bp.route('/scheduled-items', methods=['GET'])
def get_scheduled_items():
    """
    Get list of scheduled items
    """
    try:
        items = scheduler.get_scheduled_items()
        return jsonify({
            'status': 'success',
            'data': items,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error getting scheduled items: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500 