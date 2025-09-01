from flask import Blueprint, request, jsonify
from API.db_connect import get_db
from API.app.translation_service import HybridTranslationService
import asyncio
import time

addtofavorite_bp = Blueprint('addtofavorite', __name__)

@addtofavorite_bp.route('/API/addtofavorite', methods=['POST'])
def addtofavorite():
    db = get_db()
    data = request.get_json()

    # Validate input
    if not data.get('userid') or not data.get('userid').strip():
        return jsonify({'status': 'error', 'message': 'User ID is required'}), 400

    userid = data.get('userid', '').strip()
    action = data.get('action', '').strip()
    language = data.get('language', 'en').lower()  # Get language parameter
    
    # Validate action parameter
    if not action:
        return jsonify({'status': 'error', 'message': 'Action is required'}), 400
    
    if action not in ['add', 'get']:
        return jsonify({'status': 'error', 'message': 'Invalid action. Use "add" or "get"'}), 400
    
    if action == 'get':
        query = """
            SELECT fd.marketid, d.name
            FROM favorite_markets fd
            JOIN markets d ON fd.marketid = d.id
            WHERE fd.user_id = %s AND fd.isFavorite = 1
        """
        cursor = db.cursor()
        cursor.execute(query, (userid,))
        rows = cursor.fetchall()
        
        favorites = []
        for row in rows:
            favorites.append({
                'district_id': str(row['marketid']),
                'district_name': row['name']
            })
        
        # Translate district names if language is specified
        if language in ['hi', 'gu'] and favorites:  # Hindi or Gujarati
            # Use the HybridTranslationService for accurate translations
            translated_favorites = asyncio.run(
                HybridTranslationService.batch_hybrid_translate(favorites, language, 'district_name')
            )
            return jsonify({'status': 'success', 'favorites': translated_favorites})
        else:
            # Return original data for English or unsupported languages
            return jsonify({'status': 'success', 'favorites': favorites})

    # For add action, validate marketid
    if not data.get('marketid') or not data.get('marketid').strip():
        return jsonify({'status': 'error', 'message': 'District ID is required for action "add"'}), 400

    marketid = data.get('marketid', '').strip()
    cursor = db.cursor()

    # Check if record exists
    check_query = "SELECT isFavorite FROM favorite_markets WHERE user_id = %s AND marketid = %s"
    cursor.execute(check_query, (userid, marketid))
    result = cursor.fetchone()

    if result:
        # Record exists, toggle the status
        current_status = result['isFavorite']
        new_status = 0 if current_status == 1 else 1
        
        update_query = "UPDATE favorite_markets SET isFavorite = %s WHERE user_id = %s AND marketid = %s"
        try:
            cursor.execute(update_query, (new_status, userid, marketid))
            db.commit()
            return jsonify({
                'status': 'success',
                'message': 'Added to favorites' if new_status == 1 else 'Removed from favorites',
                'isFavorite': new_status
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': 'Toggle failed'})
    else:
        # First-time insert
        insert_query = "INSERT INTO favorite_markets (user_id, marketid, isFavorite) VALUES (%s, %s, 1)"
        try:
            cursor.execute(insert_query, (userid, marketid))
            db.commit()
            return jsonify({
                'status': 'success',
                'message': 'Added to favorites',
                'isFavorite': 1
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': 'Insert failed'})