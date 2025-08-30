# Configuration (app and database settings)
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 1136))
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_NAME = os.getenv('DB_NAME', 'khedutbazaar')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'SorathiyaRooT@123')

    print(f"Loaded config: DB_HOST={DB_HOST}, DB_NAME={DB_NAME}, DB_USER={DB_USER}, DB_PASSWORD={DB_PASSWORD}")
    
    @staticmethod
    def get_db_connection_params():
        return {
            'host': Config.DB_HOST,
            'port': Config.DB_PORT,
            'database': Config.DB_NAME,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD,
            'charset': 'utf8mb4',
            'autocommit': True
        }