 # Automated Scraping Scheduler
import schedule
import time
import json
import os
import traceback
from datetime import datetime
from threading import Thread
from app.automated_scraper import AutomatedScraper

class ScrapingScheduler:
    def __init__(self, config_file='scraping_config.json'):
        self.config_file = config_file
        self.scraper = AutomatedScraper()
        self.is_running = False
        self.scheduler_thread = None
        
    def load_config(self):
        """
        Load scraping configuration from JSON file
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                print(f"[INFO] Loaded configuration from {self.config_file}")
                return config
            else:
                # Create default configuration
                default_config = {
                    "enabled": True,
                    "schedule_time": "21:00",  # 9 PM
                    "states_to_scrape": [],
                    "delay_between_requests": 3,
                    "max_retries": 3,
                    "log_file": "scraping_scheduler.log",
                    "description": "Only add state IDs here. The system will automatically get all districts for each state and scrape commodity data."
                }
                self.save_config(default_config)
                print(f"[INFO] Created default configuration file: {self.config_file}")
                return default_config
        except Exception as e:
            print(f"[ERROR] Error loading configuration: {e}")
            return None
    
    def save_config(self, config):
        """
        Save scraping configuration to JSON file
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"[INFO] Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"[ERROR] Error saving configuration: {e}")
    
    def add_state_to_schedule(self, state_id):
        """
        Add a state ID to the scheduled scraping list
        """
        config = self.load_config()
        if config and state_id not in config.get('states_to_scrape', []):
            config.setdefault('states_to_scrape', []).append(state_id)
            self.save_config(config)
            print(f"[INFO] Added state ID {state_id} to scheduled scraping")
            return True
        return False
    
    def remove_state_from_schedule(self, state_id):
        """
        Remove a state ID from the scheduled scraping list
        """
        config = self.load_config()
        if config and state_id in config.get('states_to_scrape', []):
            config['states_to_scrape'].remove(state_id)
            self.save_config(config)
            print(f"[INFO] Removed state ID {state_id} from scheduled scraping")
            return True
        return False
    
    def get_scheduled_items(self):
        """
        Get list of scheduled items
        """
        config = self.load_config()
        if config:
            return {
                'states_to_scrape': config.get('states_to_scrape', []),
                'schedule_time': config.get('schedule_time', '21:00'),
                'enabled': config.get('enabled', True)
            }
        return {}
    
    def run_scheduled_scraping(self):
        """
        Run the scheduled scraping tasks - only for states
        """
        try:
            print(f"[INFO] Starting scheduled scraping at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            config = self.load_config()
            if not config or not config.get('enabled', True):
                print("[INFO] Scheduled scraping is disabled")
                return
            
            # Scrape states (this will automatically get all districts for each state)
            states_to_scrape = config.get('states_to_scrape', [])
            for state_id in states_to_scrape:
                try:
                    print(f"[INFO] Scraping state ID: {state_id}")
                    result = self.scraper.scrape_state_by_id(state_id)
                    print(f"[INFO] State scraping result: {result['status']}")
                    
                    # Add delay between requests
                    time.sleep(config.get('delay_between_requests', 3))
                    
                except Exception as e:
                    print(f"[ERROR] Error scraping state {state_id}: {e}")
                    traceback.print_exc()
                    continue
            
            print(f"[INFO] Completed scheduled scraping at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"[ERROR] Error in scheduled scraping: {e}")
            traceback.print_exc()
    
    def start_scheduler(self):
        """
        Start the scheduler in a separate thread
        """
        if self.is_running:
            print("[WARNING] Scheduler is already running")
            return False
        
        config = self.load_config()
        if not config or not config.get('enabled', True):
            print("[INFO] Scheduler is disabled in configuration")
            return False
        
        schedule_time = config.get('schedule_time', '21:00')
        
        # Schedule the job
        schedule.every().day.at(schedule_time).do(self.run_scheduled_scraping)
        
        print(f"[INFO] Scheduler started - will run daily at {schedule_time}")
        print(f"[INFO] Scheduled items: {self.get_scheduled_items()}")
        
        self.is_running = True
        
        # Start scheduler in a separate thread
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.scheduler_thread = Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        return True
    
    def stop_scheduler(self):
        """
        Stop the scheduler
        """
        if not self.is_running:
            print("[WARNING] Scheduler is not running")
            return False
        
        self.is_running = False
        schedule.clear()
        print("[INFO] Scheduler stopped")
        return True
    
    def get_scheduler_status(self):
        """
        Get current scheduler status
        """
        config = self.load_config()
        return {
            'is_running': self.is_running,
            'enabled': config.get('enabled', True) if config else False,
            'schedule_time': config.get('schedule_time', '21:00') if config else '21:00',
            'scheduled_states': config.get('states_to_scrape', []) if config else [],
            'next_run': f"Today at {config.get('schedule_time', '21:00')}" if config and config.get('enabled', True) else 'Not scheduled'
        }
    
    def run_now(self):
        """
        Run scheduled scraping immediately
        """
        print("[INFO] Running scheduled scraping immediately...")
        self.run_scheduled_scraping()

# Global scheduler instance
scheduler = ScrapingScheduler() 