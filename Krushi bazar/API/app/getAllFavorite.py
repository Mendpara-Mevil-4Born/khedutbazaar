from flask import Blueprint, request, jsonify
from API.db_connect import get_db
from API.app.translation_service import HybridTranslationService
import asyncio
import time

getAllFavorite_bp = Blueprint('getAllFavorite', __name__)

@getAllFavorite_bp.route('/API/getAllFavorite', methods=['POST'])
def getAllFavorite():
    db = get_db()
    data = request.get_json()
    user_id = data.get('user_id', '').strip()
    language = data.get('language', 'en').lower()  # Get language parameter

    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID required'})

    cursor = db.cursor()
    query = """
        SELECT m.id AS market_id, m.name AS market_name, d.name AS district_name, s.name AS state_name
        FROM favorite_markets fm
        LEFT JOIN markets m ON fm.marketid = m.id
        LEFT JOIN districts d ON m.district_id = d.id
        LEFT JOIN states s ON d.state_id = s.id
        WHERE fm.user_id = %s AND fm.isFavorite = 1
        ORDER BY fm.updated_at DESC
    """
    cursor.execute(query, (user_id,))
    favorites = cursor.fetchall()  # DictCursor automatically returns dictionaries

    # Convert market_id to string for each favorite
    for favorite in favorites:
        favorite['market_id'] = str(favorite['market_id'])

    if favorites:
        # Translate data if language is specified
        if language in ['hi', 'gu']:  # Hindi or Gujarati
            # Use the HybridTranslationService for accurate translations
            # First translate market names
            data_with_translated_markets = asyncio.run(
                HybridTranslationService.batch_hybrid_translate(favorites, language, 'market_name')
            )
            # Then translate district names
            data_with_translated_districts = asyncio.run(
                HybridTranslationService.batch_hybrid_translate(data_with_translated_markets, language, 'district_name')
            )
            # Finally translate state names
            translated_data = asyncio.run(
                HybridTranslationService.batch_hybrid_translate(data_with_translated_districts, language, 'state_name')
            )
            return jsonify({'status': 'success', 'data': translated_data})
        else:
            # Return original data for English or unsupported languages
            return jsonify({'status': 'success', 'data': favorites})
    else:
        return jsonify({'status': 'error', 'message': 'No favorites found'})