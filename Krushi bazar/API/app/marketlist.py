from flask import Blueprint, request, jsonify
from API.db_connect import get_db
import aiohttp
import asyncio
import time

marketlist_bp = Blueprint('marketlist', __name__)

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

async def batch_translate_markets_async(markets_data, target_lang):
    """Async batch translation for market, district, and state names"""
    try:
        if target_lang in ['hi', 'gu']:  # Hindi or Gujarati
            # Extract all unique names for translation
            all_names = []
            name_mapping = {}  # To track which names belong to which fields
            
            for market in markets_data:
                for field in ['market_name', 'district_name', 'state_name']:
                    name = market[field]
                    if name not in name_mapping:
                        name_mapping[name] = []
                        all_names.append(name)
                    name_mapping[name].append(field)
            
            # Check cache first
            cache_key = f"markets_{target_lang}_{','.join(all_names)}"
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
            
            # Apply translations to markets
            translated_markets = []
            for market in markets_data:
                translated_market = market.copy()
                for field in ['market_name', 'district_name', 'state_name']:
                    translated_market[field] = translation_dict[market[field]]
                translated_markets.append(translated_market)
            
            return translated_markets
        else:
            return markets_data  # Return original if language not supported
    except Exception as e:
        print(f"Batch translation error: {e}")
        return markets_data  # Return original on translation error

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
    markets = cursor.fetchall()  # DictCursor automatically returns dictionaries
    
    if markets:
        # Translate market names if language is specified
        if language in ['hi', 'gu']:  # Hindi or Gujarati
            # Run async batch translation
            translated_markets = asyncio.run(batch_translate_markets_async(markets, language))
            return jsonify({'status': 'success', 'data': translated_markets})
        else:
            # Return original data for English or unsupported languages
            return jsonify({'status': 'success', 'data': markets})
    else:
        return jsonify({'status': 'error', 'message': 'No markets found for the given district'})