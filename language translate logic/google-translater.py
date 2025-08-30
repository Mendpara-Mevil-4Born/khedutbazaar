import asyncio
import aiohttp
import requests
import json
import warnings
from urllib3.exceptions import InsecureRequestWarning

warnings.simplefilter('ignore', InsecureRequestWarning)  # suppress SSL warnings for testing

# Async function to query Google Translate unofficial API
async def translate_text_async(session, text, target_lang):
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

async def fetch_and_translate_async(userid, stateid, target_lang, output_file):
    # Fetch original data synchronously (API has no async endpoint)
    url = 'https://khedut-bazaar.4born.com/API/marketlist.php'
    headers = {'Content-Type': 'application/json'}
    payload = {"userid": userid, "stateid": stateid}

    response = requests.post(url, json=payload, headers=headers, verify=False)
    response.raise_for_status()
    data = response.json()

    items = data.get('data', [])

    results = []

    async with aiohttp.ClientSession() as session:
        # Create tasks for each translatable field in each item
        tasks = []
        for item in items:
            translated_item = item.copy()
            for field in ['market_name', 'district_name', 'state_name']:
                if field in item:
                    task = asyncio.ensure_future(
                        translate_text_async(session, item[field], target_lang)
                    )
                    tasks.append((task, translated_item, field))
            results.append(translated_item)

        # Gather translations
        translations = await asyncio.gather(*(t[0] for t in tasks))

        # Assign translations back to items
        for (task, translated_item, field), translated_text in zip(tasks, translations):
            translated_item[field] = translated_text

    # Save translated data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"Async translation completed and saved to {output_file}")

# Run async translation
if __name__ == "__main__":
    userid = "1"
    stateid = 11
    target_lang = "gu"  # Hindi
    output_file = "translated_markets_async.json"

    asyncio.run(fetch_and_translate_async(userid, stateid, target_lang, output_file))
