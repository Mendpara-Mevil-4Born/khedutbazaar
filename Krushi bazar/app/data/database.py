# Database operations
import pymysql
from pymysql import cursors
from datetime import datetime
from app.config import Config

class Database:
    def __init__(self):
        self.config = Config
        self.init_database()
    
    def get_connection(self):
        try:
            conn = pymysql.connect(**self.config.get_db_connection_params(), cursorclass=cursors.DictCursor)
            return conn
        except Exception as e:
            print(f"[ERROR] Database connection error: {e}")
            raise
    
    def init_database(self):
        try:
            # Connect without specifying database to create it if needed
            conn = pymysql.connect(
                host=self.config.DB_HOST,
                port=self.config.DB_PORT,
                user=self.config.DB_USER,
                password=self.config.DB_PASSWORD,
                charset='utf8mb4',
                cursorclass=cursors.DictCursor
            )
            cursor = conn.cursor()
            try:
                # Create database if it doesn't exist
                cursor.execute(f'CREATE DATABASE IF NOT EXISTS {self.config.DB_NAME}')
                cursor.execute(f'USE {self.config.DB_NAME}')
                
                # Create states table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS states (
                        id INT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_state_name (name)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                ''')
                print("[SUCCESS] States table initialized")

                # Create districts table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS districts (
                        id INT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        state_id INT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (state_id) REFERENCES states (id) ON DELETE CASCADE,
                        UNIQUE KEY unique_district_state (name, state_id),
                        INDEX idx_district_name (name)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                ''')
                print("[SUCCESS] Districts table initialized")

                # Create markets table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS markets (
                        id INT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        district_id INT NOT NULL,
                        state_id INT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (district_id) REFERENCES districts (id) ON DELETE CASCADE,
                        FOREIGN KEY (state_id) REFERENCES states (id) ON DELETE CASCADE,
                        UNIQUE KEY unique_market_district (name, district_id),
                        INDEX idx_market_name (name)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                ''')
                print("[SUCCESS] Markets table initialized")

                # Create commodity_prices table with state_id, district_id, market_id and last_updated
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS commodity_prices (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        state_id INT NOT NULL,
                        district_id INT NOT NULL,
                        market_id INT NOT NULL,
                        commodity VARCHAR(100) NOT NULL,
                        variety VARCHAR(100) NOT NULL,
                        min_price INT NOT NULL,
                        max_price INT NOT NULL,
                        modal_price INT NOT NULL,
                        price_date VARCHAR(50) NOT NULL,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (state_id) REFERENCES states (id) ON DELETE CASCADE,
                        FOREIGN KEY (district_id) REFERENCES districts (id) ON DELETE CASCADE,
                        FOREIGN KEY (market_id) REFERENCES markets (id) ON DELETE CASCADE,
                        INDEX idx_commodity_market (market_id, commodity),
                        UNIQUE KEY unique_price (state_id, district_id, market_id, commodity, variety, price_date)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                ''')
                print("[SUCCESS] Commodity prices table initialized")

                # Check if old columns exist and migrate data if needed
                cursor.execute("SHOW COLUMNS FROM commodity_prices LIKE 'state'")
                if cursor.fetchone():
                    print("[INFO] Migrating old commodity_prices table structure...")
                    # Add new columns if they don't exist
                    cursor.execute("SHOW COLUMNS FROM commodity_prices LIKE 'state_id'")
                    if not cursor.fetchone():
                        cursor.execute("ALTER TABLE commodity_prices ADD COLUMN state_id INT")
                        cursor.execute("ALTER TABLE commodity_prices ADD COLUMN district_id INT")
                        cursor.execute("ALTER TABLE commodity_prices ADD COLUMN market_id INT")
                        cursor.execute("ALTER TABLE commodity_prices ADD COLUMN last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
                        
                        # Update existing records with IDs
                        cursor.execute("""
                            UPDATE commodity_prices cp 
                            JOIN states s ON LOWER(cp.state) = LOWER(s.name)
                            SET cp.state_id = s.id
                        """)
                        
                        cursor.execute("""
                            UPDATE commodity_prices cp 
                            JOIN districts d ON LOWER(cp.district) = LOWER(d.name) AND cp.state_id = d.state_id
                            SET cp.district_id = d.id
                        """)
                        
                        cursor.execute("""
                            UPDATE commodity_prices cp 
                            JOIN markets m ON LOWER(cp.market) = LOWER(m.name) AND cp.district_id = m.district_id
                            SET cp.market_id = m.id
                        """)
                        
                        # Drop old unique key first to avoid conflicts
                        try:
                            cursor.execute("ALTER TABLE commodity_prices DROP INDEX unique_price")
                        except:
                            pass  # Index might not exist
                        
                        # Drop old columns
                        cursor.execute("ALTER TABLE commodity_prices DROP COLUMN state")
                        cursor.execute("ALTER TABLE commodity_prices DROP COLUMN district")
                        cursor.execute("ALTER TABLE commodity_prices DROP COLUMN market")
                        
                        # Add foreign key constraints
                        cursor.execute("ALTER TABLE commodity_prices ADD CONSTRAINT fk_commodity_state FOREIGN KEY (state_id) REFERENCES states (id) ON DELETE CASCADE")
                        cursor.execute("ALTER TABLE commodity_prices ADD CONSTRAINT fk_commodity_district FOREIGN KEY (district_id) REFERENCES districts (id) ON DELETE CASCADE")
                        cursor.execute("ALTER TABLE commodity_prices ADD CONSTRAINT fk_commodity_market FOREIGN KEY (market_id) REFERENCES markets (id) ON DELETE CASCADE")
                        
                        # Add new unique key
                        cursor.execute("ALTER TABLE commodity_prices ADD UNIQUE KEY unique_price (state_id, district_id, market_id, commodity, variety, price_date)")
                        
                        print("[SUCCESS] Migration completed")

                conn.commit()
                print("[SUCCESS] All database tables initialized successfully")
            except Exception as e:
                print(f"[ERROR] Error initializing database tables: {e}")
                conn.rollback()
                raise
            finally:
                conn.close()
        except Exception as e:
            print(f"[ERROR] Error connecting to database: {e}")
            raise
    
    def insert_state(self, state_id, name):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO states (id, name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE name = VALUES(name)',
                (state_id, name.strip())
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting state {name}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def insert_district(self, district_id, name, state_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO districts (id, name, state_id) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE name = VALUES(name)',
                (district_id, name.strip(), state_id)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting district {name}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def insert_market(self, market_id, name, district_id, state_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO markets (id, name, district_id, state_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE name = VALUES(name)',
                (market_id, name.strip(), district_id, state_id)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting market {name}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def insert_commodity_price(self, state_id, district_id, market_id, commodity, variety, min_price, max_price, modal_price, price_date):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                '''
                INSERT INTO commodity_prices
                (state_id, district_id, market_id, commodity, variety, min_price, max_price, modal_price, price_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    min_price = VALUES(min_price),
                    max_price = VALUES(max_price),
                    modal_price = VALUES(modal_price),
                    price_date = VALUES(price_date),
                    last_updated = CURRENT_TIMESTAMP
                ''',
                (state_id, district_id, market_id, commodity.strip(), variety.strip(),
                 min_price, max_price, modal_price, price_date.strip())
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting commodity price {commodity} ({variety}): {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_state_id_by_name(self, state_name):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT id FROM states WHERE LOWER(name) = LOWER(%s)', (state_name.strip(),))
            result = cursor.fetchone()
            return result['id'] if result else None
        except Exception as e:
            print(f"Error getting state ID for {state_name}: {e}")
            return None
        finally:
            conn.close()

    def get_district_id_by_name(self, district_name, state_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'SELECT id FROM districts WHERE LOWER(name) = LOWER(%s) AND state_id = %s',
                (district_name.strip(), state_id)
            )
            result = cursor.fetchone()
            return result['id'] if result else None
        except Exception as e:
            print(f"Error getting district ID for {district_name}: {e}")
            return None
        finally:
            conn.close()

    def get_market_id_by_name(self, market_name, district_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'SELECT id FROM markets WHERE LOWER(name) = LOWER(%s) AND district_id = %s',
                (market_name.strip(), district_id)
            )
            result = cursor.fetchone()
            return result['id'] if result else None
        except Exception as e:
            print(f"Error getting market ID for {market_name}: {e}")
            return None
        finally:
            conn.close()
    
    def get_all_states(self):
        conn = self.get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute('SELECT id, name FROM states ORDER BY name')
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting states: {e}")
            return []
        finally:
            conn.close()

    def get_state_by_id(self, state_id):
        conn = self.get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute('SELECT id, name FROM states WHERE id = %s', (state_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error getting state by ID: {e}")
            return None
        finally:
            conn.close()
    
    def get_districts_by_state(self, state_id):
        conn = self.get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute(
                'SELECT id, name FROM districts WHERE state_id = %s ORDER BY name',
                (state_id,)
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting districts: {e}")
            return []
        finally:
            conn.close()
    
    def get_markets_by_district(self, district_id):
        conn = self.get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute(
                'SELECT id, name FROM markets WHERE district_id = %s ORDER BY name',
                (district_id,)
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting markets: {e}")
            return []
        finally:
            conn.close()
    
    def get_markets_by_state_and_district(self, state_id, district_id):
        conn = self.get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute(
                'SELECT id, name FROM markets WHERE state_id = %s AND district_id = %s ORDER BY name',
                (state_id, district_id)
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting markets: {e}")
            return []
        finally:
            conn.close()
    
    def get_markets_by_state(self, state_id):
        conn = self.get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute('''
                SELECT m.id, m.name, m.district_id, m.state_id, d.name as district_name
                FROM markets m
                JOIN districts d ON m.district_id = d.id
                WHERE m.state_id = %s
                ORDER BY d.name, m.name
            ''', (state_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting markets by state: {e}")
            return []
        finally:
            conn.close()
    
    def get_all_districts(self):
        conn = self.get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute('SELECT id, name, state_id FROM districts ORDER BY name')
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting all districts: {e}")
            return []
        finally:
            conn.close()
    
    def search_locations(self, query):
        conn = self.get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            results = {'states': [], 'districts': [], 'markets': []}
            # Search states
            cursor.execute('SELECT id, name FROM states WHERE name LIKE %s ORDER BY name', (f'%{query}%',))
            results['states'] = cursor.fetchall()
            # Search districts
            cursor.execute('''
                SELECT d.id, d.name, d.state_id, s.name as state_name
                FROM districts d
                JOIN states s ON d.state_id = s.id
                WHERE d.name LIKE %s
                ORDER BY d.name
            ''', (f'%{query}%',))
            results['districts'] = cursor.fetchall()
            # Search markets
            cursor.execute('''
                SELECT m.id, m.name, m.district_id, m.state_id, d.name as district_name, s.name as state_name
                FROM markets m
                JOIN districts d ON m.district_id = d.id
                JOIN states s ON m.state_id = s.id
                WHERE m.name LIKE %s
                ORDER BY m.name
            ''', (f'%{query}%',))
            results['markets'] = cursor.fetchall()
            return results
        except Exception as e:
            print(f"Error searching locations: {e}")
            return {'states': [], 'districts': [], 'markets': []}
        finally:
            conn.close()
    
    def clear_all_data(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM commodity_prices')
            cursor.execute('DELETE FROM markets')
            cursor.execute('DELETE FROM districts')
            cursor.execute('DELETE FROM states')
            conn.commit()
            print("[SUCCESS] All data cleared from database")
        except Exception as e:
            print(f"Error clearing data: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def clear_states_only(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM states')
            conn.commit()
            print("[SUCCESS] States data cleared from database")
        except Exception as e:
            print(f"Error clearing states: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def clear_districts_only(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM districts')
            conn.commit()
            print("[SUCCESS] Districts data cleared from database")
        except Exception as e:
            print(f"Error clearing districts: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def clear_markets_only(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM markets')
            conn.commit()
            print("[SUCCESS] Markets data cleared from database")
        except Exception as e:
            print(f"Error clearing markets: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def clear_commodity_prices_only(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM commodity_prices')
            conn.commit()
            print("[SUCCESS] Commodity prices data cleared from database")
        except Exception as e:
            print(f"Error clearing commodity prices: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT COUNT(*) as count FROM states')
            states_count = cursor.fetchone()['count']
            cursor.execute('SELECT COUNT(*) as count FROM districts')
            districts_count = cursor.fetchone()['count']
            cursor.execute('SELECT COUNT(*) as count FROM markets')
            markets_count = cursor.fetchone()['count']
            cursor.execute('SELECT COUNT(*) as count FROM commodity_prices')
            commodities_count = cursor.fetchone()['count']
            return {
                'states': states_count,
                'districts': districts_count,
                'markets': markets_count,
                'commodities': commodities_count
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {'states': 0, 'districts': 0, 'markets': 0, 'commodities': 0}
        finally:
            conn.close()