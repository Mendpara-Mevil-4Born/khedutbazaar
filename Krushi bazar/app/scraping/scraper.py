# Consolidated scraper logic
import re
import traceback
import requests
import time
import urllib.parse
from bs4 import BeautifulSoup
from app.data.database import Database

class AgriplusScraper:
    def __init__(self):
        self.db = Database()
        self.base_url = "https://agriplus.in/prices/all"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def normalize_name_for_url(self, name):
        """Normalize name for URL formation, handling special characters"""
        # Handle parentheses by replacing them with hyphens and removing extra spaces
        # Example: "Vadodara(Baroda)" → "Vadodara-Baroda"
        name = re.sub(r'\(([^)]*)\)', r'-\1', name)
        # Replace spaces and special characters with hyphens
        name = re.sub(r'[^\w\s-]', '', name)
        name = re.sub(r'[-\s]+', '-', name)
        # Convert to lowercase and remove leading/trailing hyphens
        return name.lower().strip('-')

    def extract_states_from_html(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        states = []
        state_selects = soup.find_all('select', {'id': ['substate_id', 'state']})
        
        for select in state_selects:
            options = select.find_all('option')
            for option in options:
                value = option.get('value', '').strip()
                name = option.get_text().strip()
                if value and value != '' and value != '0' and name and name.lower() not in ['select state', 'any state']:
                    try:
                        state_id = int(value)
                        clean_name = re.sub(r'\s+', ' ', name).strip()
                        if clean_name and clean_name not in ['demo1', 'demodemo1', 'malavan']:
                            states.append({'id': state_id, 'name': clean_name})
                    except ValueError:
                        continue
        
        unique_states = {}
        for state in states:
            if state['id'] not in unique_states:
                unique_states[state['id']] = state
        return list(unique_states.values())

    def get_districts_for_state(self, state_id):
        try:
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_token = soup.find('input', {'name': '_token'})
            csrf_value = csrf_token['value'] if csrf_token else ''
            
            url = "https://agriplus.in/district/fetch"
            form_data = {
                'stateid': str(state_id),
                'id': 'district',
                '_token': csrf_value
            }
            response = self.session.post(url, data=form_data, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            districts = []
            
            options = soup.find_all('option')
            for option in options:
                value = option.get('value', '').strip()
                name = option.get_text().strip()
                if value and value != '' and value != '0' and name and name.lower() not in ['any district', 'select district']:
                    try:
                        district_id = int(value)
                        clean_name = re.sub(r'\s+', ' ', name).strip().replace('&nbsp;', ' ').strip()
                        if clean_name:
                            districts.append({'id': district_id, 'name': clean_name, 'state_id': state_id})
                    except ValueError:
                        continue
            return districts
        except Exception as e:
            print(f"[ERROR] Error getting districts for state {state_id}: {e}")
            return []

    def get_markets_for_district(self, state_id, district_id):
        try:
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_token = soup.find('input', {'name': '_token'})
            csrf_value = csrf_token['value'] if csrf_token else ''
            
            url = "https://agriplus.in/market/fetch"
            form_data = {
                'distid': str(district_id),
                'id': 'market',
                '_token': csrf_value
            }
            response = self.session.post(url, data=form_data, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            markets = []
            
            options = soup.find_all('option')
            for option in options:
                value = option.get('value', '').strip()
                name = option.get_text().strip()
                if value and value != '' and value != '0' and name and name.lower() not in ['any market', 'select market']:
                    try:
                        market_id = int(value)
                        clean_name = re.sub(r'\s+', ' ', name).strip().replace('&nbsp;', ' ').strip()
                        if clean_name:
                            markets.append({'id': market_id, 'name': clean_name, 'district_id': district_id, 'state_id': state_id})
                    except ValueError:
                        continue
            return markets
        except Exception as e:
            print(f"[ERROR] Error getting markets for district {district_id}: {e}")
            return []

    def scrape_states_only(self):
        print("Starting states scraping from website...")
        try:
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            states = self.extract_states_from_html(response.text)
            print(f"Found {len(states)} states")
            
            for state in states:
                self.db.insert_state(state['id'], state['name'])
                print(f"[SUCCESS] Saved state: {state['name']} (ID: {state['id']})")
            
            print("[SUCCESS] States scraped and saved to database")
            stats = self.db.get_stats()
            print(f"Database Statistics after states scraping:")
            print(f"  States: {stats['states']}")
            print(f"  Districts: {stats['districts']}")
            print(f"  Markets: {stats['markets']}")
            return True
        except Exception as e:
            print(f"[ERROR] Error scraping states: {e}")
            return False

    def scrape_districts_only(self):
        print("Starting districts scraping for all states...")
        try:
            states = self.db.get_all_states()
            if not states:
                print("[ERROR] No states found in database. Please scrape states first.")
                return False
            total_districts = 0
            for state in states:
                print(f"Scraping districts for {state['name']} (ID: {state['id']})...")
                districts = self.get_districts_for_state(state['id'])
                if districts:
                    for district in districts:
                        self.db.insert_district(district['id'], district['name'], district['state_id'])
                        total_districts += 1
                    print(f"[SUCCESS] Found {len(districts)} districts for {state['name']}")
                else:
                    print(f"No districts found for {state['name']}")
                time.sleep(2)
            print(f"[SUCCESS] Total {total_districts} districts saved to database")
            stats = self.db.get_stats()
            print(f"Database Statistics after districts scraping:")
            print(f"  States: {stats['states']}")
            print(f"  Districts: {stats['districts']}")
            print(f"  Markets: {stats['markets']}")
            return True
        except Exception as e:
            print(f"[ERROR] Error scraping districts: {e}")
            return False

    def scrape_markets_only(self):
        print("Starting markets scraping for all districts...")
        try:
            states = self.db.get_all_states()
            if not states:
                print("[ERROR] No states found in database. Please scrape states first.")
                return False
            total_markets = 0
            for state in states:
                print(f"Scraping markets for {state['name']} (ID: {state['id']})...")
                districts = self.db.get_districts_by_state(state['id'])
                if not districts:
                    print(f"No districts found for {state['name']}")
                    continue
                for district in districts:
                    print(f"Scraping markets for {district['name']} district...")
                    markets = self.get_markets_for_district(state['id'], district['id'])
                    if markets:
                        for market in markets:
                            self.db.insert_market(market['id'], market['name'], market['district_id'], market['state_id'])
                            total_markets += 1
                        print(f"[SUCCESS] Found {len(markets)} markets for {district['name']}")
                    else:
                        print(f"No markets found for {district['name']}")
                    time.sleep(1)
                time.sleep(2)
            print(f"[SUCCESS] Total {total_markets} markets saved to database")
            stats = self.db.get_stats()
            print(f"Database Statistics after markets scraping:")
            print(f"  States: {stats['states']}")
            print(f"  Districts: {stats['districts']}")
            print(f"  Markets: {stats['markets']}")
            return True
        except Exception as e:
            print(f"[ERROR] Error scraping markets: {e}")
            return False

    def scrape_markets_for_state(self, state_id):
        print(f"Starting markets scraping for state ID {state_id}...")
        try:
            state = self.db.get_state_by_id(state_id)
            if not state:
                print(f"[ERROR] State with ID {state_id} not found in database.")
                return False
            print(f"Scraping markets for {state['name']} (ID: {state['id']})...")
            districts = self.db.get_districts_by_state(state['id'])
            if not districts:
                print(f"No districts found for {state['name']}")
                return False
            total_markets = 0
            for district in districts:
                print(f"Scraping markets for {district['name']} district...")
                markets = self.get_markets_for_district(state['id'], district['id'])
                if markets:
                    for market in markets:
                        self.db.insert_market(market['id'], market['name'], market['district_id'], market['state_id'])
                        total_markets += 1
                    print(f"[SUCCESS] Found {len(markets)} markets for {district['name']}")
                else:
                    print(f"No markets found for {district['name']}")
                time.sleep(1)
            print(f"[SUCCESS] Total {total_markets} markets saved to database for {state['name']}")
            stats = self.db.get_stats()
            print(f"Database Statistics after markets scraping:")
            print(f"  States: {stats['states']}")
            print(f"  Districts: {stats['districts']}")
            print(f"  Markets: {stats['markets']}")
            return True
        except Exception as e:
            print(f"[ERROR] Error scraping markets for state {state_id}: {e}")
            return False

    def scrape_yard_data(self, state, district, market):
        print(f"Starting yard data scraping for {state}/{district}/{market}...")
        try:
            # Normalize names for URL with proper handling of special characters
            state_slug = self.normalize_name_for_url(state)
            district_slug = self.normalize_name_for_url(district)
            market_slug = self.normalize_name_for_url(market)
            url = f"{self.base_url}/{state_slug}/{district_slug}/{market_slug}"
            print(f"Requesting URL: {url}")
            
            response = self.session.get(url, timeout=30)
            print(f"HTTP Status: {response.status_code}")
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the commodity prices table
            table = soup.find('table')
            if not table:
                print(f"[ERROR] No commodity prices table found for {state}/{district}/{market}")
                return False

            # Fetch IDs for state, district, and market
            state_id = self.db.get_state_id_by_name(state)
            if not state_id:
                print(f"[ERROR] State {state} not found in database")
                return False
            district_id = self.db.get_district_id_by_name(district, state_id)
            if not district_id:
                print(f"[ERROR] District {district} not found in state {state}")
                return False
            market_id = self.db.get_market_id_by_name(market, district_id)
            if not market_id:
                print(f"[ERROR] Market {market} not found in district {district}")
                return False

            rows = table.find_all('tr')[1:]  # Skip header row
            commodities = []
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 10:  # Ensure enough columns (including Sl no.)
                    commodity_data = {
                        'commodity': cells[4].get_text().strip(),
                        'variety': cells[5].get_text().strip(),
                        'min_price': int(re.sub(r'[^\d]', '', cells[6].get_text().strip())),
                        'max_price': int(re.sub(r'[^\d]', '', cells[7].get_text().strip())),
                        'modal_price': int(re.sub(r'[^\d]', '', cells[8].get_text().strip())),
                        'price_date': cells[9].get_text().strip()
                    }
                    commodities.append(commodity_data)
                    if self.db.insert_commodity_price(
                        state_id,
                        district_id,
                        market_id,
                        commodity_data['commodity'],
                        commodity_data['variety'],
                        commodity_data['min_price'],
                        commodity_data['max_price'],
                        commodity_data['modal_price'],
                        commodity_data['price_date']
                    ):
                        print(f"[SUCCESS] Saved commodity: {commodity_data['commodity']} ({commodity_data['variety']}) for market {market}")
                    else:
                        print(f"[ERROR] Failed to save commodity: {commodity_data['commodity']} ({commodity_data['variety']}) for market {market}")

            if not commodities:
                print(f"[ERROR] No valid commodity data found for {state}/{district}/{market}")
                return False

            print(f"[SUCCESS] Scraped {len(commodities)} commodities for {state}/{district}/{market}")
            stats = self.db.get_stats()
            print(f"Database Statistics after yard scraping:")
            print(f"  States: {stats['states']}")
            print(f"  Districts: {stats['districts']}")
            print(f"  Markets: {stats['markets']}")
            print(f"  Commodities: {stats['commodities']}")
            time.sleep(1)  # Add delay to avoid overwhelming the server
            return True
        except Exception as e:
            print(f"[ERROR] Error scraping yard data for {state}/{district}/{market}: {e}")
            traceback.print_exc()
            return False

    def scrape_district_data(self, state, district):
        print(f"Starting district data scraping for {state}/{district}...")
        try:
            # Normalize names for URL with proper handling of special characters
            state_slug = self.normalize_name_for_url(state)
            district_slug = self.normalize_name_for_url(district)
            url = f"{self.base_url}/{state_slug}/{district_slug}"
            print(f"Requesting URL: {url}")
            
            response = self.session.get(url, timeout=30)
            print(f"HTTP Status: {response.status_code}")
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the commodity prices table
            table = soup.find('table')
            if not table:
                print(f"[ERROR] No commodity prices table found for {state}/{district}")
                return False

            # Fetch IDs for validation
            state_id = self.db.get_state_id_by_name(state)
            if not state_id:
                print(f"[ERROR] State {state} not found in database")
                return False
            district_id = self.db.get_district_id_by_name(district, state_id)
            if not district_id:
                print(f"[ERROR] District {district} not found in state {state}")
                return False

            # Get all markets for this district
            markets = self.db.get_markets_by_state_and_district(state_id, district_id)
            if not markets:
                print(f"[ERROR] No markets found for district {district}")
                return False

            rows = table.find_all('tr')[1:]  # Skip header row
            commodities = []
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 10:  # Ensure enough columns
                    market_name = cells[3].get_text().strip()
                    # Find market ID by name
                    market = next((m for m in markets if m['name'].lower() == market_name.lower()), None)
                    if not market:
                        print(f"[WARNING] Market {market_name} not found in database for district {district}")
                        continue
                    
                    commodity_data = {
                        'commodity': cells[4].get_text().strip(),
                        'variety': cells[5].get_text().strip(),
                        'min_price': int(re.sub(r'[^\d]', '', cells[6].get_text().strip())),
                        'max_price': int(re.sub(r'[^\d]', '', cells[7].get_text().strip())),
                        'modal_price': int(re.sub(r'[^\d]', '', cells[8].get_text().strip())),
                        'price_date': cells[9].get_text().strip()
                    }
                    commodities.append(commodity_data)
                    
                    if self.db.insert_commodity_price(
                        state_id,
                        district_id,
                        market['id'],
                        commodity_data['commodity'],
                        commodity_data['variety'],
                        commodity_data['min_price'],
                        commodity_data['max_price'],
                        commodity_data['modal_price'],
                        commodity_data['price_date']
                    ):
                        print(f"[SUCCESS] Saved commodity: {commodity_data['commodity']} ({commodity_data['variety']}) for market {market_name}")
                    else:
                        print(f"[ERROR] Failed to save commodity: {commodity_data['commodity']} ({commodity_data['variety']}) for market {market_name}")

            if not commodities:
                print(f"[ERROR] No valid commodity data found for {state}/{district}")
                return False

            print(f"[SUCCESS] Scraped {len(commodities)} commodities for {state}/{district}")
            stats = self.db.get_stats()
            print(f"Database Statistics after district scraping:")
            print(f"  States: {stats['states']}")
            print(f"  Districts: {stats['districts']}")
            print(f"  Markets: {stats['markets']}")
            print(f"  Commodities: {stats['commodities']}")
            time.sleep(1)  # Add delay to avoid overwhelming the server
            return True
        except Exception as e:
            print(f"[ERROR] Error scraping district data for {state}/{district}: {e}")
            traceback.print_exc()
            return False