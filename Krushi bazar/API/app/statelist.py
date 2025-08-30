from flask import Blueprint, jsonify, request
from API.db_connect import get_db
import aiohttp
import asyncio
import time

statelist_bp = Blueprint('statelist', __name__)

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

async def batch_translate_states_async(state_names, target_lang):
    """Async batch translation for multiple state names"""
    try:
        if target_lang in ['hi', 'gu']:  # Hindi or Gujarati
            # Check cache first
            cache_key = f"{target_lang}_{','.join(state_names)}"
            if cache_key in translation_cache:
                return translation_cache[cache_key]
            
            # Create async session and translate all names in parallel
            async with aiohttp.ClientSession() as session:
                tasks = [translate_text_async(session, name, target_lang) for name in state_names]
                translated_names = await asyncio.gather(*tasks)
            
            # Cache the result
            translation_cache[cache_key] = translated_names
            
            return translated_names
        else:
            return state_names  # Return original if language not supported
    except Exception as e:
        print(f"Batch translation error: {e}")
        return state_names  # Return original on translation error

@statelist_bp.route('/API/statelist', methods=['POST'])
def statelist():
    db = get_db()
    
    # Get language parameter from JSON body, default to 'en' (English)
    data = request.get_json() or {}
    language = data.get('language', 'en').lower()
    
    cursor = db.cursor()
    query = "SELECT id, name FROM states"
    cursor.execute(query)
    states = cursor.fetchall()  # DictCursor automatically returns dictionaries
    
    if states:
        # Translate state names if language is specified
        if language in ['hi', 'gu']:  # Hindi or Gujarati
            # Extract all state names for batch translation
            state_names = [state['name'] for state in states]
            
            # Run async batch translation
            translated_names = asyncio.run(batch_translate_states_async(state_names, language))
            
            # Create translated states list
            translated_states = []
            for i, state in enumerate(states):
                translated_state = state.copy()
                translated_state['name'] = translated_names[i]
                translated_states.append(translated_state)
            
            return jsonify({'status': 'success', 'data': translated_states})
        else:
            # Return original data for English or unsupported languages
            return jsonify({'status': 'success', 'data': states})
    else:
        return jsonify({'status': 'error', 'message': 'No states found'})