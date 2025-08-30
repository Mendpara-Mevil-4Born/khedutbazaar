from flask import Blueprint, jsonify, request
from datetime import datetime
from app.scraping.scraper import AgriplusScraper
from app.data.database import Database

yard_bp = Blueprint('yard', __name__, url_prefix='/scrape/yard')

@yard_bp.route('/', methods=['GET'])
def scrape_yard():
    try:
        # Get query parameters
        state_id = request.args.get('state_id')
        district_id = request.args.get('district_id')
        market_id = request.args.get('market_id')

        # Validate parameters
        if not all([state_id, district_id]):
            return jsonify({
                'status': 'error',
                'message': 'Missing required parameters: state_id, district_id',
                'timestamp': datetime.now().isoformat()
            }), 400

        # Convert to integers
        try:
            state_id = int(state_id)
            district_id = int(district_id)
            if market_id:
                market_id = int(market_id)
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': 'Invalid parameter format: state_id, district_id, and market_id (if provided) must be integers',
                'timestamp': datetime.now().isoformat()
            }), 400

        # Fetch names from database
        db = Database()
        state = db.get_state_by_id(state_id)
        if not state:
            return jsonify({
                'status': 'error',
                'message': f'State with ID {state_id} not found',
                'timestamp': datetime.now().isoformat()
            }), 404

        districts = db.get_districts_by_state(state_id)
        district = next((d for d in districts if d['id'] == district_id), None)
        if not district:
            return jsonify({
                'status': 'error',
                'message': f'District with ID {district_id} not found in state {state["name"]}',
                'timestamp': datetime.now().isoformat()
            }), 404

        # Initialize scraper and results
        scraper = AgriplusScraper()
        results = {'successful': [], 'failed': []}
        stats = db.get_stats()

        if market_id:
            # Scrape single market
            markets = db.get_markets_by_state_and_district(state_id, district_id)
            market = next((m for m in markets if m['id'] == market_id), None)
            if not market:
                return jsonify({
                    'status': 'error',
                    'message': f'Market with ID {market_id} not found in district {district["name"]}',
                    'timestamp': datetime.now().isoformat()
                }), 404

            success = scraper.scrape_yard_data(state['name'], district['name'], market['name'])
            if success:
                results['successful'].append(f"{state['name']}/{district['name']}/{market['name']}")
            else:
                results['failed'].append(f"{state['name']}/{district['name']}/{market['name']}")
        else:
            # Scrape district-level page
            success = scraper.scrape_district_data(state['name'], district['name'])
            if success:
                results['successful'].append(f"{state['name']}/{district['name']}")
            else:
                results['failed'].append(f"{state['name']}/{district['name']}")

        # Prepare response
        stats = db.get_stats()  # Refresh stats after scraping
        if results['successful']:
            status = 'success' if not results['failed'] else 'partial_success'
            message = f"Scraped data for {len(results['successful'])} locations successfully"
            if results['failed']:
                message += f", {len(results['failed'])} locations failed"
        else:
            status = 'error'
            message = 'No data scraped successfully'

        return jsonify({
            'status': status,
            'message': message,
            'successful_locations': results['successful'],
            'failed_locations': results['failed'],
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        }), 200 if results['successful'] else 404

    except Exception as e:
        if "Table 'khedutbazaar.commodity_prices' doesn't exist" in str(e):
            return jsonify({
                'status': 'error',
                'message': 'Database error: commodity_prices table does not exist',
                'timestamp': datetime.now().isoformat()
            }), 500
        return jsonify({
            'status': 'error',
            'message': f'Unexpected error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500