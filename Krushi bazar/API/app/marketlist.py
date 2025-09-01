from flask import Blueprint, request, jsonify
from API.db_connect import get_db
from API.app.translation_service import HybridTranslationService
import asyncio

marketlist_bp = Blueprint('marketlist', __name__)

@marketlist_bp.route('/API/marketlist', methods=['POST'])
def marketlist():
    db = get_db()
    data = request.get_json()
    stateid = data.get('stateid', '').strip() if data.get('stateid') else None
    userid = data.get('userid', '').strip() if data.get('userid') else None
    language = data.get('language', 'en').lower()  # Get language parameter

    cursor = db.cursor()
    if stateid:
        query = """
            SELECT m.id AS market_id, m.name AS market_name, d.name AS district_name, s.name AS state_name
            FROM markets m
            JOIN districts d ON m.district_id = d.id
            JOIN states s ON d.state_id = s.id
            WHERE m.state_id = %s
        """
        cursor.execute(query, (stateid,))
    else:
        query = """
            SELECT m.id AS market_id, m.name AS market_name, d.name AS district_name, s.name AS state_name
            FROM markets m
            JOIN districts d ON m.district_id = d.id
            JOIN states s ON d.state_id = s.id
        """
        cursor.execute(query)
    rows = cursor.fetchall()

    if rows:
        markets = []
        for row in rows:
            markets.append({
                'market_id': str(row['market_id']),
                'market_name': row['market_name'],
                'district_name': row['district_name'],
                'state_name': row['state_name']
            })

        # Translate markets if language is specified
        if language in ['hi', 'gu'] and markets:  # Hindi or Gujarati
            # Use the HybridTranslationService for accurate translations
            # First translate market names
            data_with_translated_markets = asyncio.run(
                HybridTranslationService.batch_hybrid_translate(markets, language, 'market_name')
            )
            # Then translate district names
            data_with_translated_districts = asyncio.run(
                HybridTranslationService.batch_hybrid_translate(data_with_translated_markets, language, 'district_name')
            )
            # Finally translate state names
            translated_markets = asyncio.run(
                HybridTranslationService.batch_hybrid_translate(data_with_translated_districts, language, 'state_name')
            )
            
            return jsonify({'status': 'success', 'data': translated_markets})
        else:
            # Return original data for English or unsupported languages
            return jsonify({'status': 'success', 'data': markets})
    else:
        return jsonify({'status': 'error', 'message': 'No markets found'})