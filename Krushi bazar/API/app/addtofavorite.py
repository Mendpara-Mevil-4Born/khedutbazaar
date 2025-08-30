from flask import Blueprint, request, jsonify
from API.db_connect import get_db
import aiohttp
import asyncio
import time

addtofavorite_bp = Blueprint('addtofavorite', __name__)

# Simple in-memory cache for translations
translation_cache = {}

async def translate_text_async(session, text, target_lang):
    """Fast translation using unofficial Google Translate API"""
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "en",
        "tl": target_lang,
        "dt": "t",
        "q": text
    }
    try:
        async with session.get(url, params=params) as response:
            res = await response.json()
            # Extract translated text from response structure
            translated = "".join([item[0] for item in res[0]])
            return translated
    except Exception as e:
        print(f"Error translating '{text}': {e}")
        return text

async def batch_translate_favorites_async(favorites_data, target_lang):
    """Async batch translation for favorite district names"""
    try:
        if target_lang in ['hi', 'gu']:  # Hindi or Gujarati
            # Extract all unique district names for translation
            all_names = []
            name_mapping = {}  # To track which names belong to which items
            
            for favorite in favorites_data:
                name = favorite['district_name']
                if name not in name_mapping:
                    name_mapping[name] = []
                    all_names.append(name)
                name_mapping[name].append(favorite)
            
            # Check cache first
            cache_key = f"favorites_{target_lang}_{','.join(all_names)}"
            if cache_key in translation_cache:
                translated_names = translation_cache[cache_key]
            else:
                # Create async session and translate all unique names in parallel
                async with aiohttp.ClientSession() as session:
                    tasks = [translate_text_async(session, name, target_lang) for name in all_names]
                    translated_names = await asyncio.gather(*tasks)
                
                # Cache the result
                translation_cache[cache_key] = translated_names
            
            # Create translation dictionary
            translation_dict = dict(zip(all_names, translated_names))
            
            # Apply translations to favorites
            translated_favorites = []
            for favorite in favorites_data:
                translated_favorite = favorite.copy()
                translated_favorite['district_name'] = translation_dict[favorite['district_name']]
                translated_favorites.append(translated_favorite)
            
            return translated_favorites
        else:
            return favorites_data  # Return original if language not supported
    except Exception as e:
        print(f"Batch translation error: {e}")
        return favorites_data  # Return original on translation error

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
                'district_id': row['marketid'],
                'district_name': row['name']
            })
        
        # Translate district names if language is specified
        if language in ['hi', 'gu'] and favorites:  # Hindi or Gujarati
            # Run async batch translation
            translated_favorites = asyncio.run(batch_translate_favorites_async(favorites, language))
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