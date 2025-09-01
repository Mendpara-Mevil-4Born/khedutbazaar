from flask import Blueprint, request, jsonify
from API.db_connect import get_db
from API.app.translation_service import HybridTranslationService
import asyncio

districtlist_bp = Blueprint('districtlist', __name__)

@districtlist_bp.route('/API/districtlist', methods=['POST'])
def districtlist():
    db = get_db()
    data = request.get_json()
    state_id = data.get('state_id', '').strip()
    language = data.get('language', 'en').lower()  # Get language parameter

    if not state_id:
        return jsonify({'status': 'error', 'message': 'State ID is required'})

    cursor = db.cursor()
    cursor.execute("SELECT id, name FROM districts WHERE state_id = %s ORDER BY name", (state_id,))
    rows = cursor.fetchall()

    if rows:
        districts = []
        for row in rows:
            districts.append({
                'id': str(row['id']),
                'name': row['name']
            })

        # Translate districts if language is specified
        if language in ['hi', 'gu'] and districts:  # Hindi or Gujarati
            # Use the HybridTranslationService for accurate translations
            translated_districts = asyncio.run(
                HybridTranslationService.batch_hybrid_translate(districts, language, 'name')
            )
            return jsonify({'status': 'success', 'data': translated_districts})
        else:
            # Return original data for English or unsupported languages
            return jsonify({'status': 'success', 'data': districts})
    else:
        return jsonify({'status': 'error', 'message': 'No districts found'})