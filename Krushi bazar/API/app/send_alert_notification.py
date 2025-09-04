from flask import Blueprint, jsonify
from API.db_connect import get_db
import firebase_admin
from firebase_admin import credentials, messaging
import pymysql
import os
import time

send_alert_notification_bp = Blueprint('send_alert_notification', __name__)

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK with service account"""
    try:
        # Check if Firebase is already initialized
        if not firebase_admin._apps:
            # Get the path to the firebase.json file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            api_dir = os.path.dirname(current_dir)
            firebase_config_path = os.path.join(api_dir, 'firebase.json')
            
            if os.path.exists(firebase_config_path):
                cred = credentials.Certificate(firebase_config_path)
                firebase_admin.initialize_app(cred)
                print("Firebase Admin SDK initialized successfully")
                print(f"Project: {cred.project_id}")
                print(f"Service Account: {cred.service_account_email}")
                return True
            else:
                print(f"Firebase config file not found at: {firebase_config_path}")
                return False
        else:
            print("Firebase Admin SDK already initialized")
            return True
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return False

def sendFCM(token, title, body):
    """Send Firebase Cloud Message notification using Admin SDK"""
    try:
        # Initialize Firebase if not already done
        if not initialize_firebase():
            return False
            
        # Create the message
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data={
                'title': title,
                'body': body,
                'timestamp': str(int(time.time())),
                'source': 'khedut-bazaar',
                'click_action': 'FLUTTER_NOTIFICATION_CLICK'
            },
            token=token
        )
        
        # Send the message
        response = messaging.send(message)
        print(f"FCM notification sent successfully. Message ID: {response}")
        return True
        
    except messaging.UnregisteredError:
        print(f"FCM token is invalid or expired: {token[:20]}...")
        return False
    except messaging.InvalidArgumentError as e:
        print(f"Invalid FCM token format: {e}")
        return False
    except messaging.QuotaExceededError:
        print(f"FCM quota exceeded")
        return False
    except Exception as e:
        print(f"Error sending FCM notification: {e}")
        return False

@send_alert_notification_bp.route('/API/send_alert_notification', methods=['GET'])
def send_alert_notification():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM alerts")
    alerts = cursor.fetchall()  # DictCursor automatically returns dictionaries

    for alert in alerts:
        userid = alert['userid']
        marketid = alert['marketid']
        commodity = alert['commodity']
        condition = alert['conditions']
        amount = alert['amount']

        price_query = """
            SELECT modal_price FROM commodity_prices
            WHERE market_id = %s AND commodity = %s
            ORDER BY price_date DESC LIMIT 1
        """
        cursor.execute(price_query, (marketid, commodity))
        price_row = cursor.fetchone()
        if not price_row:
            continue
        latest_price = int(price_row['modal_price'] / 5)  # Match PHP: use int() instead of round()

        shouldNotify = False
        if condition == 'greater' and latest_price > float(amount):
            shouldNotify = True
        if condition == 'less' and latest_price < float(amount):
            shouldNotify = True

        if shouldNotify:
            token_query = "SELECT token FROM login WHERE id = %s AND token IS NOT NULL"
            cursor.execute(token_query, (userid,))
            token_row = cursor.fetchone()
            if not token_row:
                continue
            sendFCM(token_row['token'], "Price Alert", f"Price of {commodity} in market {marketid} is Rs.{latest_price} (your alert: {condition} {amount})")

    return jsonify({'status': 'done'})

# Test endpoint for development
@send_alert_notification_bp.route('/API/test_notification', methods=['POST'])
def test_notification():
    """Test endpoint to send a notification to a specific token"""
    try:
        from flask import request
        data = request.get_json()
        token = data.get('token')
        title = data.get('title', 'Test Notification')
        body = data.get('body', 'This is a test notification')
        
        if not token:
            return jsonify({'status': 'error', 'message': 'Token is required'}), 400
        
        success = sendFCM(token, title, body)
        
        if success:
            return jsonify({'status': 'success', 'message': 'Test notification sent'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to send test notification'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500