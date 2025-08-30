from flask import Blueprint, request, jsonify
from API.db_connect import get_db
import aiohttp
import asyncio
import time

getCommodityBasedOnmarket_bp = Blueprint('getCommodityBasedOnmarket', __name__)

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

async def batch_translate_commodities_async(commodities_data, target_lang):
    """Async batch translation for commodity and variety names"""
    try:
        if target_lang in ['hi', 'gu']:  # Hindi or Gujarati
            # Extract all unique text fields for translation
            all_texts = []
            text_mapping = {}  # To track which texts belong to which fields and items
            
            for item in commodities_data:
                # Collect commodity names
                commodity = item['commodity']
                if commodity not in text_mapping:
                    text_mapping[commodity] = {'type': 'commodity', 'items': []}
                    all_texts.append(commodity)
                text_mapping[commodity]['items'].append(item)
                
                # Collect variety names
                variety = item['variety']
                if variety not in text_mapping:
                    text_mapping[variety] = {'type': 'variety', 'items': []}
                    all_texts.append(variety)
                text_mapping[variety]['items'].append(item)
            
            # Check cache first
            cache_key = f"commodities_{target_lang}_{','.join(all_texts)}"
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
            
            # Apply translations to commodities data
            translated_commodities_data = []
            for item in commodities_data:
                translated_item = item.copy()
                translated_item['commodity'] = translation_dict[item['commodity']]
                translated_item['variety'] = translation_dict[item['variety']]
                translated_commodities_data.append(translated_item)
            
            return translated_commodities_data
        else:
            return commodities_data  # Return original if language not supported
    except Exception as e:
        print(f"Batch translation error: {e}")
        return commodities_data  # Return original on translation error

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
    
    # Translate data if language is specified
    if language in ['hi', 'gu'] and commodities_data:  # Hindi or Gujarati
        # Run async batch translation
        translated_data = asyncio.run(batch_translate_commodities_async(commodities_data, language))
        return jsonify({'status': 'success', 'data': translated_data})
    else:
        # Return original data for English or unsupported languages
        return jsonify({'status': 'success', 'data': commodities_data})