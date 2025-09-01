from flask import Blueprint, request, jsonify
from API.db_connect import get_db
from API.app.translation_service import HybridTranslationService
import asyncio

statelist_bp = Blueprint('statelist', __name__)

@statelist_bp.route('/API/statelist', methods=['POST'])
def statelist():
    db = get_db()
    data = request.get_json()
    language = data.get('language', 'en').lower()  # Get language parameter

    cursor = db.cursor()
    cursor.execute("SELECT id, name FROM states ORDER BY name")
    rows = cursor.fetchall()

    if rows:
        states = []
        for row in rows:
            states.append({
                'id': str(row['id']),
                'name': row['name']
            })

        # Translate states if language is specified
        if language in ['hi', 'gu'] and states:  # Hindi or Gujarati
            # Use the HybridTranslationService for accurate translations
            translated_states = asyncio.run(
                HybridTranslationService.batch_hybrid_translate(states, language, 'name')
            )
            return jsonify({'status': 'success', 'data': translated_states})
        else:
            # Return original data for English or unsupported languages
            return jsonify({'status': 'success', 'data': states})
    else:
        return jsonify({'status': 'error', 'message': 'No states found'})