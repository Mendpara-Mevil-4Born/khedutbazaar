from flask import Blueprint, request, jsonify
from API.db_connect import get_db
from datetime import datetime
import aiohttp
import asyncio
import time

getcrop_data_bp = Blueprint('getcrop_data', __name__)

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

async def batch_translate_crop_data_async(crop_data, target_lang):
    """Async batch translation for crop data fields"""
    try:
        if target_lang in ['hi', 'gu']:  # Hindi or Gujarati
            # Extract all unique text fields for translation
            all_texts = []
            text_mapping = {}  # To track which texts belong to which fields and items
            
            for item in crop_data:
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
                
                # Collect market names
                market_name = item['market_name']
                if market_name not in text_mapping:
                    text_mapping[market_name] = {'type': 'market_name', 'items': []}
                    all_texts.append(market_name)
                text_mapping[market_name]['items'].append(item)
                
                # Collect status messages for both Hindi and Gujarati
                status = item['status']
                if status not in text_mapping:
                    text_mapping[status] = {'type': 'status', 'items': []}
                    all_texts.append(status)
                text_mapping[status]['items'].append(item)
            
            # Check cache first
            cache_key = f"crop_data_{target_lang}_{','.join(all_texts)}"
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
            
            # Apply translations to crop data
            translated_crop_data = []
            for item in crop_data:
                translated_item = item.copy()
                translated_item['commodity'] = translation_dict[item['commodity']]
                translated_item['variety'] = translation_dict[item['variety']]
                translated_item['market_name'] = translation_dict[item['market_name']]
                # Translate status for both Hindi and Gujarati
                translated_item['status'] = translation_dict[item['status']]
                translated_crop_data.append(translated_item)
            
            return translated_crop_data
        else:
            return crop_data  # Return original if language not supported
    except Exception as e:
        print(f"Batch translation error: {e}")
        return crop_data  # Return original on translation error

def timeAgo(dt_input):
    """Handle both string and datetime inputs for timeAgo calculation"""
    if isinstance(dt_input, datetime):
        # If it's already a datetime object
        timestamp = dt_input.timestamp()
    else:
        # If it's a string, parse it
        timestamp = datetime.strptime(dt_input, '%Y-%m-%d %H:%M:%S').timestamp()
    
    diff = datetime.now().timestamp() - timestamp
    if diff < 60: return 'just now'
    if diff < 3600: return f"{int(diff/60)} minutes ago"
    if diff < 86400: return f"{int(diff/3600)} hours ago"
    if diff < 604800: return f"{int(diff/86400)} days ago"
    if diff < 2592000: return f"{int(diff/604800)} weeks ago"
    if diff < 31536000: return f"{int(diff/2592000)} months ago"
    return f"{int(diff/31536000)} years ago"

def format_price_date(date_str):
    """Handle different date formats and return consistent format"""
    try:
        # Try to parse as YYYY-MM-DD format
        if '-' in date_str and len(date_str.split('-')[0]) == 4:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return f"{date_obj.day} {date_obj.strftime('%b')}"
        else:
            # If it's already formatted like "27 Aug", return as is
            return date_str
    except:
        # If parsing fails, return the original string
        return date_str

@getcrop_data_bp.route('/API/getcrop_data', methods=['POST'])
def getcrop_data():
    db = get_db()
    data = request.get_json()
    market_id = data.get('market_id', '').strip()
    language = data.get('language', 'en').lower()  # Get language parameter

    if not market_id:
        return jsonify({'status': 'error', 'message': 'Market ID is required'}), 400

    cursor = db.cursor()
    
    # MySQL 8+ query with ROW_NUMBER using last_updated for ordering (matching PHP)
    query = """
        WITH ranked AS (
            SELECT cp.id, cp.commodity, cp.variety, cp.modal_price, cp.min_price, cp.max_price,
                   cp.price_date, cp.last_updated, m.name AS market_name,
                   ROW_NUMBER() OVER (PARTITION BY cp.commodity, cp.variety ORDER BY cp.last_updated DESC, cp.id DESC) AS rn
            FROM commodity_prices cp
            LEFT JOIN markets m ON cp.market_id = m.id
            WHERE cp.market_id = %s
        )
        SELECT * FROM ranked WHERE rn <= 2
        ORDER BY commodity, variety, rn
    """
    cursor.execute(query, (market_id,))
    rows = cursor.fetchall()

    data_map = {}  # group by commodity||variety
    for row in rows:
        key = f"{row['commodity']}||{row['variety']}"
        if key not in data_map:
            data_map[key] = {'latest': None, 'previous': None}
        if row['rn'] == 1:
            data_map[key]['latest'] = row
        elif row['rn'] == 2:
            data_map[key]['previous'] = row

    # Prepare final output
    final_data = []
    for pair in data_map.values():
        latest = pair['latest']
        previous = pair['previous']
        status = "stable"  # Start with English status
        
        if previous:
            if latest['modal_price'] > previous['modal_price']: status = "increase"
            elif latest['modal_price'] < previous['modal_price']: status = "decrease"
        
        # Use the helper function to handle date formatting
        formatted_date = format_price_date(latest['price_date'])
        
        final_data.append({
            'id': latest['id'],
            'commodity': latest['commodity'],
            'variety': latest['variety'],
            'modal_price': int(latest['modal_price'] / 5),  # Match PHP: divide by 5, no decimals
            'min_price': int(latest['min_price'] / 5),      # Match PHP: divide by 5, no decimals
            'max_price': int(latest['max_price'] / 5),      # Match PHP: divide by 5, no decimals
            'status': status,
            'price_date': formatted_date,
            'market_name': latest['market_name'],
            'last_updated': timeAgo(latest['last_updated'])
        })
    
    # Translate data if language is specified
    if language in ['hi', 'gu'] and final_data:  # Hindi or Gujarati
        # Run async batch translation
        translated_data = asyncio.run(batch_translate_crop_data_async(final_data, language))
        return jsonify({'status': 'success', 'data': translated_data})
    else:
        # Return original data for English or unsupported languages
        return jsonify({'status': 'success', 'data': final_data})