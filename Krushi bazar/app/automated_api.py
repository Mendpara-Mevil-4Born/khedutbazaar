# Automated Scraping API endpoints
from flask import Blueprint, jsonify, request
from datetime import datetime
from app.automated_scraper import AutomatedScraper

automated_bp = Blueprint('automated', __name__, url_prefix='/automated')

@automated_bp.route('/scrape/district/<int:district_id>', methods=['GET'])
def scrape_district_automated(district_id):
    """
    Automatically scrape all markets for a specific district
    """
    try:
        scraper = AutomatedScraper()
        result = scraper.scrape_district_by_id(district_id)
        
        return jsonify(result), 200 if result['status'] in ['success', 'partial_success'] else 400
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Unexpected error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@automated_bp.route('/scrape/state/<int:state_id>', methods=['GET'])
def scrape_state_automated(state_id):
    """
    Automatically scrape all districts and markets for a specific state
    """
    try:
        scraper = AutomatedScraper()
        result = scraper.scrape_state_by_id(state_id)
        
        return jsonify(result), 200 if result['status'] in ['success', 'partial_success'] else 400
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Unexpected error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@automated_bp.route('/status', methods=['GET'])
def get_automated_status():
    """
    Get automated scraping system status
    """
    try:
        scraper = AutomatedScraper()
        result = scraper.get_scraping_status()
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error getting status: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@automated_bp.route('/scrape/bulk', methods=['POST'])
def bulk_scrape():
    """
    Bulk scraping with multiple district IDs
    """
    try:
        data = request.get_json()
        if not data or 'district_ids' not in data:
            return jsonify({
                'status': 'error',
                'message': 'district_ids array is required in request body',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        district_ids = data['district_ids']
        if not isinstance(district_ids, list):
            return jsonify({
                'status': 'error',
                'message': 'district_ids must be an array',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        scraper = AutomatedScraper()
        results = []
        
        for district_id in district_ids:
            try:
                result = scraper.scrape_district_by_id(district_id)
                results.append(result)
            except Exception as e:
                results.append({
                    'status': 'error',
                    'message': f'Error scraping district {district_id}: {str(e)}',
                    'district_id': district_id,
                    'timestamp': datetime.now().isoformat()
                })
        
        # Calculate overall status
        successful = sum(1 for r in results if r['status'] == 'success')
        partial = sum(1 for r in results if r['status'] == 'partial_success')
        failed = sum(1 for r in results if r['status'] == 'error')
        
        overall_status = 'success' if failed == 0 else 'partial_success' if successful > 0 else 'error'
        
        return jsonify({
            'status': overall_status,
            'message': f'Bulk scraping completed: {successful} successful, {partial} partial, {failed} failed',
            'results': results,
            'summary': {
                'total': len(district_ids),
                'successful': successful,
                'partial_success': partial,
                'failed': failed
            },
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Unexpected error in bulk scraping: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500 