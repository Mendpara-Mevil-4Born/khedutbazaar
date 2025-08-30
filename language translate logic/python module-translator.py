import warnings
import requests
from deep_translator import GoogleTranslator
from requests.packages.urllib3.exceptions import InsecureRequestWarning

warnings.simplefilter('ignore', InsecureRequestWarning)  # suppress SSL warnings for testing

def fetch_and_translate_stream(userid, stateid, target_lang):
    url = 'https://khedut-bazaar.4born.com/API/marketlist.php'
    headers = {'Content-Type': 'application/json'}
    payload = {"userid": userid, "stateid": stateid}

    response = requests.post(url, json=payload, headers=headers, verify=False)
    response.raise_for_status()
    data = response.json()

    translator = GoogleTranslator(source='en', target=target_lang)

    for i, item in enumerate(data.get('data', []), start=1):
        translated_item = item.copy()
        for field in ['market_name', 'district_name', 'state_name']:
            if field in item:
                try:
                    translated_item[field] = translator.translate(item[field])
                except Exception as e:
                    print(f"Translation error for {field} in item {i}: {e}")
                    translated_item[field] = item[field]
        print(f"Translated item {i}:", translated_item)
        yield translated_item

# Example usage:
if __name__ == "__main__":
    userid = "1"
    stateid = 11
    target_lang = "hi"  # Hindi

    for translated_json in fetch_and_translate_stream(userid, stateid, target_lang):
        # Process each translated JSON object here if needed
        pass
