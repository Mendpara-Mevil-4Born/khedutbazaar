from flask import Blueprint, request, jsonify
from API.db_connect import get_db
from API.app.translation_service import HybridTranslationService
import asyncio

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/API/alerts', methods=['POST'])
def alerts():
    db = get_db()
    data = request.get_json()

    action = data.get('action', '').strip()
    userid = data.get('userid')
    marketid = data.get('marketid')
    commodity = data.get('commodity')
    variety = data.get('variety')

    cursor = db.cursor()

    if not action:
        return jsonify({'status': 'error', 'message': 'Action is required'})

    if action == 'add':
        if not all([userid, marketid, commodity, data.get('conditions'), data.get('amount')]):
            return jsonify({'status': 'error', 'message': 'All fields are required for add'})
        conditions = data.get('conditions')
        amount = data.get('amount')
        insert_query = """
            INSERT INTO alerts (userid, marketid, commodity, variety, conditions, amount)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (userid, marketid, commodity, variety, conditions, amount))
        db.commit()
        return jsonify({'status': 'success', 'message': 'Condition added'})

    elif action == 'delete':
        alert_id = int(data.get('id', 0))
        if alert_id <= 0:
            return jsonify({'status': 'error', 'message': 'id is required for delete'})
        delete_query = "DELETE FROM alerts WHERE id = %s"
        cursor.execute(delete_query, (alert_id,))
        db.commit()
        if cursor.rowcount > 0:
            return jsonify({'status': 'success', 'message': 'Condition deleted'})
        else:
            return jsonify({'status': 'error', 'message': 'No record found with given id'})

    elif action == 'get':
        if not userid:
            return jsonify({'status': 'error', 'message': 'userid is required for get'})
        language = data.get('language', 'en').lower()  # Get language parameter
        get_query = """
            SELECT a.*, m.name AS market_name
            FROM alerts a
            LEFT JOIN markets m ON a.marketid = m.id
            WHERE a.userid = %s
        """
        cursor.execute(get_query, (userid,))
        alerts_data = cursor.fetchall()  # DictCursor automatically returns dictionaries

        # Convert id and marketid to string
        for alert in alerts_data:
            alert['id'] = str(alert['id'])
            alert['marketid'] = str(alert['marketid'])
            alert['userid'] = str(alert['userid'])


        if alerts_data:
            # Enhanced translation logic that handles all scenarios properly
            translated_alerts = []
            
            for alert in alerts_data:
                translated_alert = alert.copy()
                
                # Define fields to translate
                fields_to_translate = ['market_name', 'commodity', 'variety', 'conditions']
                
                for field in fields_to_translate:
                    if field in translated_alert and translated_alert[field]:
                        original_value = translated_alert[field]
                        
                        if language == 'en':
                            # Translate TO English (from any source language)
                            try:
                                # Check if it's already English
                                if HybridTranslationService.is_english_text(original_value):
                                    translated_alert[field] = original_value
                                else:
                                    # Detect language and translate to English
                                    detected_lang = HybridTranslationService.detect_language_from_json(original_value)
                                    if detected_lang:
                                        translated_alert[field] = asyncio.run(
                                            HybridTranslationService.reverse_translate_to_english(original_value, detected_lang)
                                        )
                                    else:
                                        # Fallback: use Google Translate
                                        translated_alert[field] = asyncio.run(
                                            HybridTranslationService.detect_language_and_translate_to_english(original_value)
                                        )
                            except Exception as e:
                                print(f"Translation error for {field}: {e}")
                                translated_alert[field] = original_value
                                
                        elif language in ['hi', 'gu']:
                            # Translate TO Hindi/Gujarati (from any source language)
                            try:
                                # First, get English version
                                if HybridTranslationService.is_english_text(original_value):
                                    english_value = original_value
                                else:
                                    # Convert to English first
                                    detected_lang = HybridTranslationService.detect_language_from_json(original_value)
                                    if detected_lang:
                                        english_value = asyncio.run(
                                            HybridTranslationService.reverse_translate_to_english(original_value, detected_lang)
                                        )
                                    else:
                                        english_value = asyncio.run(
                                            HybridTranslationService.detect_language_and_translate_to_english(original_value)
                                        )
                                
                                # Then translate from English to target language
                                translated_alert[field] = asyncio.run(
                                    HybridTranslationService.hybrid_translate(english_value, language)
                                )
                            except Exception as e:
                                print(f"Translation error for {field}: {e}")
                                translated_alert[field] = original_value
                        # For unsupported languages, keep original data
                
                translated_alerts.append(translated_alert)
            
            return jsonify({'status': 'success', 'data': translated_alerts})
        else:
            return jsonify({'status': 'error', 'message': 'No alerts found'})

    else:
        return jsonify({'status': 'error', 'message': 'Invalid action'})