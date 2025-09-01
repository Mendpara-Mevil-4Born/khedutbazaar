from flask import Blueprint, request, jsonify
from API.db_connect import get_db
from datetime import datetime, timedelta
from API.app.translation_service import HybridTranslationService
import asyncio

commodity_stats_bp = Blueprint('commodity_stats', __name__)

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

    # Auto-detect input language and translate to English for database query
    original_commodity = commodity
    original_variety = variety
    
    # Always translate input to English for database query (regardless of input language)
    try:
        # Create temporary data for translation
        temp_data = [{'commodity': commodity, 'variety': variety}]
        
        # Auto-detect language and translate commodity to English for database query
        translated_data = asyncio.run(
            HybridTranslationService.batch_detect_and_translate_to_english(temp_data, 'commodity')
        )
        commodity = translated_data[0]['commodity']
        
        # Auto-detect language and translate variety to English for database query
        translated_data = asyncio.run(
            HybridTranslationService.batch_detect_and_translate_to_english(temp_data, 'variety')
        )
        variety = translated_data[0]['variety']
        
        print(f"Translated input - Original: {original_commodity} -> English: {commodity}")
        print(f"Translated input - Original: {original_variety} -> English: {variety}")
        
    except Exception as e:
        print(f"Translation error for input parameters: {e}")
        # If translation fails, use original values
        commodity = original_commodity
        variety = original_variety

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
            'id': str(row['id']),
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
            # Use the HybridTranslationService for accurate translations
            # First translate commodity names
            data_with_translated_commodities = asyncio.run(
                HybridTranslationService.batch_hybrid_translate(all_data, language, 'commodity')
            )
            # Then translate variety names
            data_with_translated_varieties = asyncio.run(
                HybridTranslationService.batch_hybrid_translate(data_with_translated_commodities, language, 'variety')
            )
            # Finally translate status messages
            translated_data = asyncio.run(
                HybridTranslationService.batch_hybrid_translate(data_with_translated_varieties, language, 'status')
            )
            
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