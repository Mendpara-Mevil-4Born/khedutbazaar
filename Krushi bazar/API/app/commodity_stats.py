from flask import Blueprint, request, jsonify
from API.db_connect import get_db
from datetime import datetime, timedelta
import aiohttp
import asyncio
import time

commodity_stats_bp = Blueprint('commodity_stats', __name__)

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

async def batch_translate_commodity_stats_async(stats_data, target_lang):
    """Async batch translation for commodity stats fields"""
    try:
        if target_lang in ['hi', 'gu']:  # Hindi or Gujarati
            # Extract all unique text fields for translation
            all_texts = []
            text_mapping = {}  # To track which texts belong to which fields and items
            
            for item in stats_data:
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
                
                # Collect status messages for both Hindi and Gujarati
                status = item['status']
                if status not in text_mapping:
                    text_mapping[status] = {'type': 'status', 'items': []}
                    all_texts.append(status)
                text_mapping[status]['items'].append(item)
            
            # Check cache first
            cache_key = f"commodity_stats_{target_lang}_{','.join(all_texts)}"
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
            
            # Apply translations to stats data
            translated_stats_data = []
            for item in stats_data:
                translated_item = item.copy()
                translated_item['commodity'] = translation_dict[item['commodity']]
                translated_item['variety'] = translation_dict[item['variety']]
                # Translate status for both Hindi and Gujarati
                translated_item['status'] = translation_dict[item['status']]
                translated_stats_data.append(translated_item)
            
            return translated_stats_data
        else:
            return stats_data  # Return original if language not supported
    except Exception as e:
        print(f"Batch translation error: {e}")
        return stats_data  # Return original on translation error

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

@commodity_stats_bp.route('/API/commodity_stats', methods=['POST'])
def commodity_stats():
    db = get_db()
    data = request.get_json()

    commodity = data.get('commodity', '').strip()
    variety = data.get('variety', '').strip()
    market_id = data.get('market_id', '').strip()
    days = int(data.get('days', 7))
    language = data.get('language', 'en').lower()  # Get language parameter

    # Validate required inputs (matching PHP)
    if not commodity:
        return jsonify({'status': 'error', 'message': 'Commodity is required'})
    if not market_id:
        return jsonify({'status': 'error', 'message': 'Market ID is required'})

    from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    to_date = datetime.now().strftime('%Y-%m-%d')

    cursor = db.cursor()
    query = """
        SELECT id, commodity, variety, modal_price, min_price, max_price, price_date
        FROM commodity_prices
        WHERE commodity = %s AND variety = %s AND market_id = %s
          AND last_updated BETWEEN %s AND %s
        ORDER BY last_updated ASC
    """
    cursor.execute(query, (commodity, variety, market_id, from_date, to_date))
    rows = cursor.fetchall()

    temp_data = []
    prices = []
    previous_price = None

    for row in rows:
        # status logic (matching PHP) - Start with English status
        status = "stable"
        if previous_price is not None:
            if row['modal_price'] > previous_price:
                status = "increase"
            elif row['modal_price'] < previous_price:
                status = "decrease"
        
        # Use helper function for date formatting
        formatted_date = format_price_date(row['price_date'])
        
        temp_data.append({
            'id': row['id'],
            'commodity': row['commodity'],
            'variety': row['variety'],
            'modal_price': int(row['modal_price'] / 5),  # Match PHP: divide by 5, no decimals
            'min_price': int(row['min_price'] / 5),      # Match PHP: divide by 5, no decimals
            'max_price': int(row['max_price'] / 5),      # Match PHP: divide by 5, no decimals
            'price_date': formatted_date,
            'status': status
        })
        prices.append(row['modal_price'])
        previous_price = row['modal_price']

    # Reverse the data to match PHP (newest first)
    all_data = list(reversed(temp_data))
    
    if prices:
        max_prices = [d['max_price'] for d in all_data]
        min_prices = [d['min_price'] for d in all_data]
        summary = {
            'highest_price': max(max_prices),
            'lowest_price': min(min_prices),
            'average_price': int(sum(prices) / len(prices) / 5),  # Match PHP: divide by 5, no decimals
            'total_entries': len(prices)
        }
        
        # Translate data if language is specified
        if language in ['hi', 'gu'] and all_data:  # Hindi or Gujarati
            # Run async batch translation
            translated_data = asyncio.run(batch_translate_commodity_stats_async(all_data, language))
            return jsonify({
                'status': 'success',
                'filter_days': days,
                'summary': summary,
                'data': translated_data
            })
        else:
            # Return original data for English or unsupported languages
            return jsonify({
                'status': 'success',
                'filter_days': days,
                'summary': summary,
                'data': all_data
            })
    else:
        return jsonify({'status': 'error', 'message': 'No data found for the selected filter'})