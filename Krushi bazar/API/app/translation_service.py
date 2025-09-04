# Hybrid Translation Service for Khedut Bazaar
# Combines Google Translate with JSON file translations for accuracy
import aiohttp
import asyncio
import time
import json
import os

class HybridTranslationService:
    """Hybrid translation service combining Google Translate with JSON file data"""
    
    # JSON file paths
    JSON_FILES = {
        'commodity': 'commodity.json',
        'states': 'states.json', 
        'districts': 'districts.json',
        'markets': 'markets.json',
        'variety': 'variety.json'
    }
    
    # Translation cache
    translation_cache = {}
    
    # Loaded JSON data cache
    _json_data_cache = {}
    
    @classmethod
    def _load_json_file(cls, file_type):
        """Load JSON file data with caching"""
        if file_type in cls._json_data_cache:
            return cls._json_data_cache[file_type]
        
        try:
            # Get the directory where this file is located
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to the API directory where JSON files are located
            api_dir = os.path.dirname(current_dir)
            json_file_path = os.path.join(api_dir, cls.JSON_FILES[file_type])
            
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._json_data_cache[file_type] = data
                return data
        except Exception as e:
            print(f"Error loading {file_type} JSON file: {e}")
            return None
    
    @classmethod
    def _get_translation_from_json(cls, text, target_lang, file_types=None):
        """Get translation from JSON files"""
        if file_types is None:
            file_types = ['commodity', 'states', 'districts', 'markets', 'variety']
        
        # Map language codes to JSON field names
        lang_map = {
            'hi': 'hindi',
            'gu': 'gujarati',
            'en': 'english'
        }
        
        target_field = lang_map.get(target_lang)
        if not target_field:
            return None
        
        # Search through specified JSON files
        for file_type in file_types:
            data = cls._load_json_file(file_type)
            if not data:
                continue
            
            # Get the main array from the JSON (e.g., 'commodities', 'states', etc.)
            main_key = list(data.keys())[0]  # Get the first key (e.g., 'commodities')
            items = data[main_key]
            
            # Search for the text in the appropriate field
            for item in items:
                if target_lang == 'en':
                    # If target is English, search in hindi/gujarati fields
                    if item.get('hindi') == text or item.get('gujarati') == text:
                        return item.get('english')
                else:
                    # If target is Hindi/Gujarati, search in English field
                    if item.get('english') == text:
                        return item.get(target_field)
        
        return None
    
    @classmethod
    async def translate_text_async(cls, session, text, target_lang):
        """Google Translate API call"""
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
                translated = "".join([item[0] for item in res[0]])
                return translated
        except Exception as e:
            print(f"Google Translate error for '{text}': {e}")
            return text
    
    @classmethod
    def get_local_translation(cls, text, target_lang):
        """Get translation from JSON files"""
        return cls._get_translation_from_json(text, target_lang)
    
    @classmethod
    async def hybrid_translate(cls, text, target_lang):
        """
        Hybrid translation: First check JSON files, then Google Translate
        """
        if target_lang not in ['hi', 'gu']:
            return text
        
        # First check JSON file translations
        json_translation = cls.get_local_translation(text, target_lang)
        if json_translation:
            return json_translation
        
        # If not in JSON files, use Google Translate
        async with aiohttp.ClientSession() as session:
            google_translation = await cls.translate_text_async(session, text, target_lang)
            return google_translation
    
    @classmethod
    def get_reverse_local_translation(cls, text, source_lang):
        """Get reverse translation from JSON files (Hindi/Gujarati to English)"""
        if source_lang in ['hi', 'gu']:
            return cls._get_translation_from_json(text, 'en')
        return None
    
    @classmethod
    async def reverse_translate_to_english(cls, text, source_lang):
        """
        Reverse translation: Hindi/Gujarati to English
        First check JSON files, then Google Translate
        """
        if source_lang not in ['hi', 'gu']:
            return text
        
        # First check JSON files for reverse lookup
        json_reverse = cls.get_reverse_local_translation(text, source_lang)
        if json_reverse:
            return json_reverse
        
        # If not in JSON files, use Google Translate (Hindi/Gujarati to English)
        async with aiohttp.ClientSession() as session:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                "client": "gtx",
                "sl": source_lang,  # Source language (hi or gu)
                "tl": "en",         # Target language (English)
                "dt": "t",
                "q": text
            }
            try:
                async with session.get(url, params=params) as response:
                    res = await response.json()
                    translated = "".join([item[0] for item in res[0]])
                    return translated
            except Exception as e:
                print(f"Google Translate error for '{text}': {e}")
                return text
    
    @classmethod
    async def detect_language_and_translate_to_english(cls, text):
        """
        Auto-detect language and translate to English for database queries
        Works with Hindi, Gujarati, or English input
        """
        # First check if it's already English (no translation needed)
        if cls.is_english_text(text):
            return text
        
        # Check if it's Hindi or Gujarati using JSON files
        detected_lang = cls.detect_language_from_json(text)
        if detected_lang:
            return await cls.reverse_translate_to_english(text, detected_lang)
        
        # If not found in JSON files, try Google Translate with auto-detection
        async with aiohttp.ClientSession() as session:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                "client": "gtx",
                "sl": "auto",  # Auto-detect source language
                "tl": "en",    # Target language (English)
                "dt": "t",
                "q": text
            }
            try:
                async with session.get(url, params=params) as response:
                    res = await response.json()
                    translated = "".join([item[0] for item in res[0]])
                    return translated
            except Exception as e:
                print(f"Google Translate error for '{text}': {e}")
                return text
    
    @classmethod
    def is_english_text(cls, text):
        """Check if text appears to be English"""
        # Simple heuristic: if text contains mostly ASCII characters, it's likely English
        english_chars = sum(1 for c in text if ord(c) < 128)
        return english_chars / len(text) > 0.8 if text else True
    
    @classmethod
    def detect_language_from_json(cls, text):
        """Detect language by checking JSON files"""
        # Check if text exists in Hindi translations
        for file_type in ['commodity', 'states', 'districts', 'markets', 'variety']:
            data = cls._load_json_file(file_type)
            if not data:
                continue
            
            main_key = list(data.keys())[0]
            items = data[main_key]
            
            for item in items:
                if item.get('hindi') == text:
                    return 'hi'
                if item.get('gujarati') == text:
                    return 'gu'
        
        return None
    
    @classmethod
    async def batch_detect_and_translate_to_english(cls, items, name_field='name'):
        """
        Batch auto-detect language and translate to English for database queries
        Works with Hindi, Gujarati, or English input
        """
        # Check cache first
        cache_key = f"detect_translate_{','.join([str(item.get(name_field, '')) for item in items])}"
        if cache_key in cls.translation_cache:
            return cls.translation_cache[cache_key]
        
        # Extract unique texts for translation
        unique_texts = list(set([item.get(name_field, '') for item in items if item.get(name_field, '')]))
        
        # Create async session and translate all unique texts
        async with aiohttp.ClientSession() as session:
            tasks = [cls.detect_language_and_translate_to_english(text) for text in unique_texts]
            translated_texts = await asyncio.gather(*tasks)
        
        # Create translation dictionary
        translation_dict = dict(zip(unique_texts, translated_texts))
        
        # Apply translations to items
        translated_items = []
        for item in items:
            translated_item = item.copy()
            if name_field in item:
                translated_item[name_field] = translation_dict.get(item[name_field], item[name_field])
            translated_items.append(translated_item)
        
        # Cache the result
        cls.translation_cache[cache_key] = translated_items
        return translated_items
    
    @classmethod
    async def batch_hybrid_translate(cls, items, target_lang, name_field='name'):
        """
        Batch hybrid translation for multiple items
        """
        if target_lang not in ['hi', 'gu']:
            return items
        
        # Check cache first
        cache_key = f"hybrid_{target_lang}_{','.join([str(item.get(name_field, '')) for item in items])}"
        if cache_key in cls.translation_cache:
            return cls.translation_cache[cache_key]
        
        # Extract unique texts for translation
        unique_texts = list(set([item.get(name_field, '') for item in items if item.get(name_field, '')]))
        
        # Create async session and translate all unique texts
        async with aiohttp.ClientSession() as session:
            tasks = [cls.hybrid_translate(text, target_lang) for text in unique_texts]
            translated_texts = await asyncio.gather(*tasks)
        
        # Create translation dictionary
        translation_dict = dict(zip(unique_texts, translated_texts))
        
        # Apply translations to items
        translated_items = []
        for item in items:
            translated_item = item.copy()
            if name_field in item:
                translated_item[name_field] = translation_dict.get(item[name_field], item[name_field])
            translated_items.append(translated_item)
        
        # Cache the result
        cls.translation_cache[cache_key] = translated_items
        return translated_items
    
    @classmethod
    async def batch_reverse_translate_to_english(cls, items, source_lang, name_field='name'):
        """
        Batch reverse translation: Hindi/Gujarati to English for database queries
        """
        if source_lang not in ['hi', 'gu']:
            return items
        
        # Check cache first
        cache_key = f"reverse_{source_lang}_{','.join([str(item.get(name_field, '')) for item in items])}"
        if cache_key in cls.translation_cache:
            return cls.translation_cache[cache_key]
        
        # Extract unique texts for translation
        unique_texts = list(set([item.get(name_field, '') for item in items if item.get(name_field, '')]))
        
        # Create async session and translate all unique texts
        async with aiohttp.ClientSession() as session:
            tasks = [cls.reverse_translate_to_english(text, source_lang) for text in unique_texts]
            translated_texts = await asyncio.gather(*tasks)
        
        # Create translation dictionary
        translation_dict = dict(zip(unique_texts, translated_texts))
        
        # Apply translations to items
        translated_items = []
        for item in items:
            translated_item = item.copy()
            if name_field in item:
                translated_item[name_field] = translation_dict.get(item[name_field], item[name_field])
            translated_items.append(translated_item)
        
        # Cache the result
        cls.translation_cache[cache_key] = translated_items
        return translated_items
    
    @classmethod
    def get_supported_languages(cls):
        """Get list of supported language codes"""
        return ['en', 'hi', 'gu']
    
    @classmethod
    def get_language_name(cls, lang_code):
        """Get human-readable language name from code"""
        language_names = {
            'en': 'English',
            'hi': 'हिंदी',
            'gu': 'ગુજરાતી'
        }
        return language_names.get(lang_code, lang_code)
    
    @classmethod
    def add_custom_translation(cls, text, translation, target_lang):
        """
        Add custom translation to cache
        Useful for adding new terms discovered during usage
        """
        cache_key = f"custom_{target_lang}_{text}"
        cls.translation_cache[cache_key] = translation
        print(f"Added custom translation: {text} -> {translation} ({target_lang})")
        return True
