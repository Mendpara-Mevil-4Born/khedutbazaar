from flask import Blueprint, request, jsonify
from API.db_connect import get_db
import aiohttp
import asyncio
import time

getAllFavorite_bp = Blueprint('getAllFavorite', __name__)

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
    """Async batch translation for favorite market, district, and state names"""
    try:
        if target_lang in ['hi', 'gu']:  # Hindi or Gujarati
            # Extract all unique text fields for translation
            all_texts = []
            text_mapping = {}  # To track which texts belong to which fields and items
            
            for item in favorites_data:
                # Collect market names
                market_name = item['market_name']
                if market_name not in text_mapping:
                    text_mapping[market_name] = {'type': 'market_name', 'items': []}
                    all_texts.append(market_name)
                text_mapping[market_name]['items'].append(item)
                
                # Collect district names
                district_name = item['district_name']
                if district_name not in text_mapping:
                    text_mapping[district_name] = {'type': 'district_name', 'items': []}
                    all_texts.append(district_name)
                text_mapping[district_name]['items'].append(item)
                
                # Collect state names
                state_name = item['state_name']
                if state_name not in text_mapping:
                    text_mapping[state_name] = {'type': 'state_name', 'items': []}
                    all_texts.append(state_name)
                text_mapping[state_name]['items'].append(item)
            
            # Check cache first
            cache_key = f"favorites_{target_lang}_{','.join(all_texts)}"
            if cache_key in translation_cache:
                translated_texts = translation_cache[cache_key]
            else:
                # Create async session and translate all unique texts in parallel
                async with aiohttp.ClientSession() as session:
                    tasks = [translate_text_async(session, text, target_lang) for text in all_texts]
                    translated_texts = await asyncio.gather(*tasks)
                
                # Cache the result
                translation_cache[cache_key] = translated_texts
            
            # Create translation dictionary
            translation_dict = dict(zip(all_texts, translated_texts))
            
            # Apply translations to favorites data
            translated_favorites_data = []
            for item in favorites_data:
                translated_item = item.copy()
                translated_item['market_name'] = translation_dict[item['market_name']]
                translated_item['district_name'] = translation_dict[item['district_name']]
                translated_item['state_name'] = translation_dict[item['state_name']]
                translated_favorites_data.append(translated_item)
            
            return translated_favorites_data
        else:
            return favorites_data  # Return original if language not supported
    except Exception as e:
        print(f"Batch translation error: {e}")
        return favorites_data  # Return original on translation error

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
    
    if favorites:
        # Translate data if language is specified
        if language in ['hi', 'gu']:  # Hindi or Gujarati
            # Run async batch translation
            translated_data = asyncio.run(batch_translate_favorites_async(favorites, language))
            return jsonify({'status': 'success', 'data': translated_data})
        else:
            # Return original data for English or unsupported languages
            return jsonify({'status': 'success', 'data': favorites})
    else:
        return jsonify({'status': 'error', 'message': 'No favorites found'})