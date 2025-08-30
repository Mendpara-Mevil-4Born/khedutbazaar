# Data retrieval API endpoints
from flask import Blueprint, jsonify, request
from datetime import datetime
from app.data.database import Database

data_bp = Blueprint('data', __name__, url_prefix='/api/database')

db = Database()

@data_bp.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Khedut Bazaar API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'states': '/api/database/states',
            'districts': '/api/database/states/district',
            'markets': '/api/database/states/district/markets',
            'stats': '/api/database/stats',
            'search': '/api/database/search',
            'yard': '/api/database/yard'
        }
    })

@data_bp.route('/stats')
def get_stats():
    try:
        stats = db.get_stats()
        return jsonify({
            'status': 'success',
            'data': stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@data_bp.route('/states', methods=['GET'])
def get_states():
    try:
        states = db.get_all_states()
        return jsonify({
            'status': 'success',
            'data': states,
            'count': len(states),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@data_bp.route('/states/district', methods=['POST'])
def get_districts_by_state():
    try:
        data = request.get_json()
        if not data or 'state_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'state_id is required in the request body',
                'timestamp': datetime.now().isoformat()
            }), 400
        state_id = data['state_id']
        try:
            state_id = int(state_id)
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': 'state_id must be an integer',
                'timestamp': datetime.now().isoformat()
            }), 400
        districts = db.get_districts_by_state(state_id)
        state = db.get_state_by_id(state_id)
        state_name = state['name'] if state else None
        return jsonify({
            'status': 'success',
            'data': districts,
            'count': len(districts),
            'state_id': state_id,
            'state_name': state_name,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@data_bp.route('/states/district/markets', methods=['POST'])
def get_markets_by_state_and_district():
    try:
        data = request.get_json()
        if not data or 'state_id' not in data or 'district_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'state_id and district_id are required in the request body',
                'timestamp': datetime.now().isoformat()
            }), 400
        state_id = data['state_id']
        district_id = data['district_id']
        try:
            state_id = int(state_id)
            district_id = int(district_id)
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': 'state_id and district_id must be integers',
                'timestamp': datetime.now().isoformat()
            }), 400
        markets = db.get_markets_by_state_and_district(state_id, district_id)
        state = db.get_state_by_id(state_id)
        state_name = state['name'] if state else None
        districts = db.get_districts_by_state(state_id)
        district = next((d for d in districts if d['id'] == district_id), None)
        district_name = district['name'] if district else None
        return jsonify({
            'status': 'success',
            'data': markets,
            'count': len(markets),
            'state_id': state_id,
            'state_name': state_name,
            'district_id': district_id,
            'district_name': district_name,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@data_bp.route('/districts/<int:district_id>/markets')
def get_markets_by_district(district_id):
    try:
        markets = db.get_markets_by_district(district_id)
        return jsonify({
            'status': 'success',
            'data': markets,
            'count': len(markets),
            'district_id': district_id,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@data_bp.route('/search')
def search_locations():
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({
                'status': 'error',
                'message': 'Query parameter "q" is required',
                'timestamp': datetime.now().isoformat()
            }), 400
        results = db.search_locations(query.lower())
        return jsonify({
            'status': 'success',
            'data': results,
            'query': query,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@data_bp.route('/yard', methods=['GET'])
def get_commodity_prices():
    try:
        # Get query parameters
        state_id = request.args.get('state_id')
        district_id = request.args.get('district_id')
        market_id = request.args.get('market_id')

        # Validate parameters
        if state_id:
            try:
                state_id = int(state_id)
                state = db.get_state_by_id(state_id)
                if not state:
                    return jsonify({
                        'status': 'error',
                        'message': f'State with ID {state_id} not found',
                        'data': [],
                        'count': 0,
                        'timestamp': datetime.now().isoformat()
                    }), 404
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid state_id: must be an integer',
                    'data': [],
                    'count': 0,
                    'timestamp': datetime.now().isoformat()
                }), 400

        if district_id:
            try:
                district_id = int(district_id)
                if not state_id:
                    return jsonify({
                        'status': 'error',
                        'message': 'state_id is required when district_id is provided',
                        'data': [],
                        'count': 0,
                        'timestamp': datetime.now().isoformat()
                    }), 400
                districts = db.get_districts_by_state(state_id)
                district = next((d for d in districts if d['id'] == district_id), None)
                if not district:
                    return jsonify({
                        'status': 'error',
                        'message': f'District with ID {district_id} not found in state ID {state_id}',
                        'data': [],
                        'count': 0,
                        'timestamp': datetime.now().isoformat()
                    }), 404
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid district_id: must be an integer',
                    'data': [],
                    'count': 0,
                    'timestamp': datetime.now().isoformat()
                }), 400

        if market_id:
            try:
                market_id = int(market_id)
                if not (state_id and district_id):
                    return jsonify({
                        'status': 'error',
                        'message': 'state_id and district_id are required when market_id is provided',
                        'data': [],
                        'count': 0,
                        'timestamp': datetime.now().isoformat()
                    }), 400
                markets = db.get_markets_by_state_and_district(state_id, district_id)
                market = next((m for m in markets if m['id'] == market_id), None)
                if not market:
                    return jsonify({
                        'status': 'error',
                        'message': f'Market with ID {market_id} not found in district ID {district_id}',
                        'data': [],
                        'count': 0,
                        'timestamp': datetime.now().isoformat()
                    }), 404
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid market_id: must be an integer',
                    'data': [],
                    'count': 0,
                    'timestamp': datetime.now().isoformat()
                }), 400

        # Build dynamic query with JOINs to get names
        query = '''
            SELECT cp.id, s.name as state_name, d.name as district_name, m.name as market_name, 
                   cp.commodity, cp.variety, cp.min_price, cp.max_price, 
                   cp.modal_price, cp.price_date, cp.state_id, cp.district_id, cp.market_id, 
                   cp.last_updated, cp.created_at
            FROM commodity_prices cp
            JOIN states s ON cp.state_id = s.id
            JOIN districts d ON cp.district_id = d.id
            JOIN markets m ON cp.market_id = m.id
            WHERE 1=1
        '''
        params = []
        if state_id:
            query += ' AND state_id = %s'
            params.append(state_id)
        if district_id:
            query += ' AND district_id = %s'
            params.append(district_id)
        if market_id:
            query += ' AND market_id = %s'
            params.append(market_id)
        query += ' ORDER BY created_at DESC'

        # Execute query
        conn = db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            return jsonify({
                'status': 'success',
                'message': f'Retrieved {len(results)} commodity price records',
                'data': results,
                'count': len(results),
                'state_id': state_id if state_id else None,
                'district_id': district_id if district_id else None,
                'market_id': market_id if market_id else None,
                'timestamp': datetime.now().isoformat()
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error retrieving commodity prices: {str(e)}',
                'data': [],
                'count': 0,
                'timestamp': datetime.now().isoformat()
            }), 500
        finally:
            conn.close()

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Unexpected error: {str(e)}',
            'data': [],
            'count': 0,
            'timestamp': datetime.now().isoformat()
        }), 500

@data_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'timestamp': datetime.now().isoformat()
    }), 404

@data_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500