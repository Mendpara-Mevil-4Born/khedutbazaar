from flask import Blueprint, jsonify
from datetime import datetime
from app.scraping.scraper import AgriplusScraper
from app.data.database import Database

scraping_bp = Blueprint('scraping', __name__, url_prefix='/scrape')

@scraping_bp.route('/states')
def scrape_states():
    try:
        scraper = AgriplusScraper()
        success = scraper.scrape_states_only()
        db = Database()
        stats = db.get_stats()
        if success:
            return jsonify({
                'status': 'success',
                'message': 'States data scraped from website',
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to scrape states data',
                'timestamp': datetime.now().isoformat()
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@scraping_bp.route('/districts')
def scrape_districts():
    try:
        scraper = AgriplusScraper()
        success = scraper.scrape_districts_only()
        db = Database()
        stats = db.get_stats()
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Districts data scraped for all states',
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to scrape districts data',
                'timestamp': datetime.now().isoformat()
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@scraping_bp.route('/markets')
def scrape_markets():
    try:
        scraper = AgriplusScraper()
        success = scraper.scrape_markets_only()
        db = Database()
        stats = db.get_stats()
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Markets data scraped for all districts',
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to scrape markets data',
                'timestamp': datetime.now().isoformat()
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@scraping_bp.route('/markets/<int:state_id>')
def scrape_markets_by_state(state_id):
    try:
        scraper = AgriplusScraper()
        success = scraper.scrape_markets_for_state(state_id)
        db = Database()
        state = db.get_state_by_id(state_id)
        markets = db.get_markets_by_state(state_id)
        stats = db.get_stats()
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Markets data scraped for state ID {state_id}',
                'state': state,
                'markets_scraped': len(markets),
                'markets': markets,
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Failed to scrape markets data for state ID {state_id}',
                'timestamp': datetime.now().isoformat()
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500