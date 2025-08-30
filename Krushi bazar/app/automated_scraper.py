# Automated Scraping Functionality
import time
import traceback
from datetime import datetime
from app.scraping.scraper import AgriplusScraper
from app.data.database import Database

class AutomatedScraper:
    def __init__(self):
        self.db = Database()
        self.scraper = AgriplusScraper()
    
    def scrape_district_by_id(self, district_id):
        """
        Scrape all data for a specific district by ID
        """
        try:
            print(f"[INFO] Starting automated scraping for district ID: {district_id}")
            
            # Get district information
            districts = self.db.get_all_districts()
            district = None
            state = None
            
            for d in districts:
                if d['id'] == district_id:
                    district = d
                    state = self.db.get_state_by_id(d['state_id'])
                    break
            
            if not district:
                print(f"[ERROR] District with ID {district_id} not found")
                return {
                    'status': 'error',
                    'message': f'District with ID {district_id} not found',
                    'timestamp': datetime.now().isoformat()
                }
            
            print(f"[INFO] Found district: {district['name']} in state: {state['name']}")
            
            # Get all markets for this district
            markets = self.db.get_markets_by_state_and_district(state['id'], district_id)
            if not markets:
                print(f"[WARNING] No markets found for district {district['name']}")
                return {
                    'status': 'warning',
                    'message': f'No markets found for district {district["name"]}',
                    'timestamp': datetime.now().isoformat()
                }
            
            print(f"[INFO] Found {len(markets)} markets for district {district['name']}")
            
            # Scrape data for each market
            successful_markets = []
            failed_markets = []
            total_commodities = 0
            
            for market in markets:
                try:
                    print(f"[INFO] Scraping market: {market['name']}")
                    
                    # Format URL using the scraper's normalize function
                    state_slug = self.scraper.normalize_name_for_url(state['name'])
                    district_slug = self.scraper.normalize_name_for_url(district['name'])
                    market_slug = self.scraper.normalize_name_for_url(market['name'])
                    
                    url = f"https://agriplus.in/prices/all/{state_slug}/{district_slug}/{market_slug}"
                    print(f"[INFO] Requesting URL: {url}")
                    
                    # Scrape the market data
                    success = self.scraper.scrape_yard_data(
                        state['name'], 
                        district['name'], 
                        market['name']
                    )
                    
                    if success:
                        successful_markets.append(market['name'])
                        print(f"[SUCCESS] Scraped data for market: {market['name']}")
                    else:
                        failed_markets.append(market['name'])
                        print(f"[ERROR] Failed to scrape data for market: {market['name']}")
                    
                    # Add delay to avoid overwhelming the server
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"[ERROR] Error scraping market {market['name']}: {e}")
                    failed_markets.append(market['name'])
                    traceback.print_exc()
                    continue
            
            # Get updated stats
            stats = self.db.get_stats()
            
            return {
                'status': 'success' if successful_markets else 'partial_success' if failed_markets else 'error',
                'message': f'Scraped data for {len(successful_markets)} markets successfully',
                'district_id': district_id,
                'district_name': district['name'],
                'state_id': state['id'],
                'state_name': state['name'],
                'successful_markets': successful_markets,
                'failed_markets': failed_markets,
                'total_markets': len(markets),
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[ERROR] Error in automated scraping: {e}")
            traceback.print_exc()
            return {
                'status': 'error',
                'message': f'Error in automated scraping: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def scrape_state_by_id(self, state_id):
        """
        Scrape all districts and markets for a specific state by ID
        """
        try:
            print(f"[INFO] Starting automated scraping for state ID: {state_id}")
            
            # Get state information
            state = self.db.get_state_by_id(state_id)
            if not state:
                print(f"[ERROR] State with ID {state_id} not found")
                return {
                    'status': 'error',
                    'message': f'State with ID {state_id} not found',
                    'timestamp': datetime.now().isoformat()
                }
            
            print(f"[INFO] Found state: {state['name']}")
            
            # Get all districts for this state
            districts = self.db.get_districts_by_state(state_id)
            if not districts:
                print(f"[WARNING] No districts found for state {state['name']}")
                return {
                    'status': 'warning',
                    'message': f'No districts found for state {state["name"]}',
                    'timestamp': datetime.now().isoformat()
                }
            
            print(f"[INFO] Found {len(districts)} districts for state {state['name']}")
            
            # Scrape data for each district
            successful_districts = []
            failed_districts = []
            total_commodities = 0
            
            for district in districts:
                try:
                    print(f"[INFO] Scraping district: {district['name']}")
                    
                    # Format URL using the scraper's normalize function
                    state_slug = self.scraper.normalize_name_for_url(state['name'])
                    district_slug = self.scraper.normalize_name_for_url(district['name'])
                    
                    url = f"https://agriplus.in/prices/all/{state_slug}/{district_slug}"
                    print(f"[INFO] Requesting URL: {url}")
                    
                    # Scrape the district data
                    success = self.scraper.scrape_district_data(
                        state['name'], 
                        district['name']
                    )
                    
                    if success:
                        successful_districts.append(district['name'])
                        print(f"[SUCCESS] Scraped data for district: {district['name']}")
                    else:
                        failed_districts.append(district['name'])
                        print(f"[ERROR] Failed to scrape data for district: {district['name']}")
                    
                    # Add delay to avoid overwhelming the server
                    time.sleep(3)
                    
                except Exception as e:
                    print(f"[ERROR] Error scraping district {district['name']}: {e}")
                    failed_districts.append(district['name'])
                    traceback.print_exc()
                    continue
            
            # Get updated stats
            stats = self.db.get_stats()
            
            return {
                'status': 'success' if successful_districts else 'partial_success' if failed_districts else 'error',
                'message': f'Scraped data for {len(successful_districts)} districts successfully',
                'state_id': state_id,
                'state_name': state['name'],
                'successful_districts': successful_districts,
                'failed_districts': failed_districts,
                'total_districts': len(districts),
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[ERROR] Error in automated state scraping: {e}")
            traceback.print_exc()
            return {
                'status': 'error',
                'message': f'Error in automated state scraping: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def compare_and_update_data(self, existing_data, new_data):
        """
        Compare existing data with new data and update only changed values
        """
        try:
            changes = []
            
            # Compare each field
            for field in ['min_price', 'max_price', 'modal_price', 'price_date']:
                if existing_data.get(field) != new_data.get(field):
                    changes.append({
                        'field': field,
                        'old_value': existing_data.get(field),
                        'new_value': new_data.get(field)
                    })
            
            if changes:
                print(f"[INFO] Changes detected: {changes}")
                return True, changes
            else:
                print(f"[INFO] No changes detected")
                return False, []
                
        except Exception as e:
            print(f"[ERROR] Error comparing data: {e}")
            return False, []
    
    def get_scraping_status(self):
        """
        Get current scraping status and statistics
        """
        try:
            stats = self.db.get_stats()
            return {
                'status': 'success',
                'stats': stats,
                'last_updated': datetime.now().isoformat(),
                'message': 'Scraping system is operational'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error getting scraping status: {str(e)}',
                'timestamp': datetime.now().isoformat()
            } 