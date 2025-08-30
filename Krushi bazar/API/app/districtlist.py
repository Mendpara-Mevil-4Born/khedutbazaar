from flask import Blueprint, request, jsonify
from API.db_connect import get_db
import aiohttp
import asyncio
import time

districtlist_bp = Blueprint('districtlist', __name__)

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

async def batch_translate_districts_async(district_names, target_lang):
    """Async batch translation for multiple district names"""
    try:
        if target_lang in ['hi', 'gu']:  # Hindi or Gujarati
            # Check cache first
            cache_key = f"districts_{target_lang}_{','.join(district_names)}"
            if cache_key in translation_cache:
                return translation_cache[cache_key]
            
            # Create async session and translate all names in parallel
            async with aiohttp.ClientSession() as session:
                tasks = [translate_text_async(session, name, target_lang) for name in district_names]
                translated_names = await asyncio.gather(*tasks)
            
            # Cache the result
            translation_cache[cache_key] = translated_names
            
            return translated_names
        else:
            return district_names  # Return original if language not supported
    except Exception as e:
        print(f"Batch translation error: {e}")
        return district_names  # Return original on translation error

@districtlist_bp.route('/API/districtlist', methods=['POST'])
def districtlist():
    db = get_db()
    data = request.get_json()
    state_id = data.get('state_id', '').strip()
    language = data.get('language', 'en').lower()  # Get language parameter

    cursor = db.cursor()
    if state_id:
        query = "SELECT id, name FROM districts WHERE state_id = %s"
        cursor.execute(query, (state_id,))
    else:
        query = "SELECT id, name FROM districts"
        cursor.execute(query)
    districts = cursor.fetchall()  # DictCursor automatically returns dictionaries
    
    if districts:
        # Translate district names if language is specified
        if language in ['hi', 'gu']:  # Hindi or Gujarati
            # Extract all district names for batch translation
            district_names = [district['name'] for district in districts]
            
            # Run async batch translation
            translated_names = asyncio.run(batch_translate_districts_async(district_names, language))
            
            # Create translated districts list
            translated_districts = []
            for i, district in enumerate(districts):
                translated_district = district.copy()
                translated_district['name'] = translated_names[i]
                translated_districts.append(translated_district)
            
            return jsonify({'status': 'success', 'data': translated_districts})
        else:
            # Return original data for English or unsupported languages
            return jsonify({'status': 'success', 'data': districts})
    else:
        return jsonify({'status': 'error', 'message': 'No districts found'})