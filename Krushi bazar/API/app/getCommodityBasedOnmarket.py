from flask import Blueprint, request, jsonify
from API.db_connect import get_db
from API.app.translation_service import HybridTranslationService
import asyncio
import time

getCommodityBasedOnmarket_bp = Blueprint('getCommodityBasedOnmarket', __name__)

@getCommodityBasedOnmarket_bp.route('/API/getCommodityBasedOnmarket', methods=['POST'])
def getCommodityBasedOnmarket():
    db = get_db()
    data = request.get_json()
    market_id = data.get('market_id', '').strip()
    language = data.get('language', 'en').lower()  # Get language parameter

    if not market_id:
        return jsonify({'status': 'error', 'message': 'Market ID is required'})

    cursor = db.cursor()
    query = """
        SELECT MIN(id) as id, commodity, variety
        FROM commodity_prices
        WHERE market_id = %s
        GROUP BY commodity, variety
        ORDER BY id DESC
    """
    cursor.execute(query, (market_id,))
    commodities_data = cursor.fetchall()  # DictCursor automatically returns dictionaries

    # Convert id to string for each commodity
    for commodity in commodities_data:
        commodity['id'] = str(commodity['id'])

    # Translate data if language is specified
    if language in ['hi', 'gu'] and commodities_data:  # Hindi or Gujarati
        # Use the HybridTranslationService for accurate translations
        # First translate commodity names
        data_with_translated_commodities = asyncio.run(
            HybridTranslationService.batch_hybrid_translate(commodities_data, language, 'commodity')
        )
        # Then translate variety names
        translated_data = asyncio.run(
            HybridTranslationService.batch_hybrid_translate(data_with_translated_commodities, language, 'variety')
        )
        return jsonify({'status': 'success', 'data': translated_data})
    else:
        # Return original data for English or unsupported languages
        return jsonify({'status': 'success', 'data': commodities_data})