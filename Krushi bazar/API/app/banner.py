from flask import Blueprint, jsonify, request
from API.db_connect import get_db
from API.app.translation_service import HybridTranslationService
import asyncio

banner_bp = Blueprint('banner', __name__)

@banner_bp.route('/API/banner', methods=['POST'])
def banner():
    db = get_db()
    data = request.get_json()
    
    # Set English as default if no language is provided
    requested_language = data.get('language', 'en').lower() if data.get('language') else 'en'
    
    cursor = db.cursor()
    
    # Step 1: First get banners from database matching the requested language
    query = "SELECT id, description, title, language FROM banner WHERE language = %s"
    cursor.execute(query, (requested_language,))
    banners = cursor.fetchall()
    
    if not banners:
        return jsonify({'status': 'error', 'message': f'No banners found for language: {requested_language}'})
    
    # Step 2: Process the retrieved data and apply translation logic if needed
    processed_banners = []
    
    for banner in banners:
        banner_dict = {
            'id': str(banner['id']),
            'title': banner['title'],
            'description': banner['description'],
            'language': banner['language']
        }
        
        # Always detect the actual language of content, regardless of database language field
        title_actual_lang = HybridTranslationService.detect_language_from_json(banner['title'])
        desc_actual_lang = HybridTranslationService.detect_language_from_json(banner['description'])
        
        # If language detection fails, assume it's the database language
        if not title_actual_lang:
            title_actual_lang = banner['language']
        if not desc_actual_lang:
            desc_actual_lang = banner['language']
        
        # If user requested Hindi or Gujarati, translate English content to that language
        if requested_language in ['hi', 'gu']:
            # Translate title if it's in English
            if title_actual_lang == 'en' or HybridTranslationService.is_english_text(banner['title']):
                try:
                    translated_title = asyncio.run(
                        HybridTranslationService.hybrid_translate(banner['title'], requested_language)
                    )
                    banner_dict['title'] = translated_title
                    banner_dict['original_title_language'] = 'en'
                except Exception as e:
                    print(f"Title translation error: {e}")
                    # Keep original title if translation fails
            
            # Translate description if it's in English
            if desc_actual_lang == 'en' or HybridTranslationService.is_english_text(banner['description']):
                try:
                    translated_description = asyncio.run(
                        HybridTranslationService.hybrid_translate(banner['description'], requested_language)
                    )
                    banner_dict['description'] = translated_description
                    banner_dict['original_description_language'] = 'en'
                except Exception as e:
                    print(f"Description translation error: {e}")
                    # Keep original description if translation fails
            
            # If content is already in the requested language, keep it as is
            # But if it's in a different non-English language, translate to requested language
            if title_actual_lang not in ['en', requested_language]:
                try:
                    # Translate from other language to English first, then to requested language
                    english_title = asyncio.run(
                        HybridTranslationService.reverse_translate_to_english(banner['title'], title_actual_lang)
                    )
                    translated_title = asyncio.run(
                        HybridTranslationService.hybrid_translate(english_title, requested_language)
                    )
                    banner_dict['title'] = translated_title
                    banner_dict['original_title_language'] = title_actual_lang
                except Exception as e:
                    print(f"Title translation error: {e}")
            
            if desc_actual_lang not in ['en', requested_language]:
                try:
                    # Translate from other language to English first, then to requested language
                    english_description = asyncio.run(
                        HybridTranslationService.reverse_translate_to_english(banner['description'], desc_actual_lang)
                    )
                    translated_description = asyncio.run(
                        HybridTranslationService.hybrid_translate(english_description, requested_language)
                    )
                    banner_dict['description'] = translated_description
                    banner_dict['original_description_language'] = desc_actual_lang
                except Exception as e:
                    print(f"Description translation error: {e}")
        
        processed_banners.append(banner_dict)
    
    return jsonify({
        'status': 'success', 
        'data': processed_banners,
        'requested_language': requested_language,
        'total_banners': len(processed_banners)
    })