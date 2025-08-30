from flask import Blueprint, jsonify
from API.db_connect import get_db
import requests

send_alert_notification_bp = Blueprint('send_alert_notification', __name__)

def sendFCM(token, title, body):
    serverKey = 'YOUR_FIREBASE_SERVER_KEY'
    url = 'https://fcm.googleapis.com/fcm/send'
    headers = {
        'Authorization': f'key={serverKey}',
        'Content-Type': 'application/json'
    }
    payload = {
        'to': token,
        'notification': {
            'title': title,
            'body': body
        }
    }
    requests.post(url, json=payload, headers=headers)

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
            sendFCM(token_row['token'], "Price Alert", f"Price of {commodity} in market {marketid} is ₹{latest_price} (your alert: {condition} {amount})")

    return jsonify({'status': 'done'})