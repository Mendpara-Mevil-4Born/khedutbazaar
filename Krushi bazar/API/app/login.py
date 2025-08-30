from flask import Blueprint, request, jsonify
from API.db_connect import get_db  # <-- Change this import
import pymysql

login_bp = Blueprint('login', __name__)

@login_bp.route('/API/login', methods=['POST'])
def login():
    db = get_db()
    data = request.get_json()
    device_id = data.get('device_id', '').strip()
    token = data.get('token', '').strip() if data.get('token') else None

    if not device_id:
        return jsonify({'status': 'error', 'message': 'Device ID is required'}), 400

    cursor = db.cursor(pymysql.cursors.DictCursor)  # <-- Use DictCursor
    check_query = "SELECT * FROM login WHERE device_id = %s"
    cursor.execute(check_query, (device_id,))
    result = cursor.fetchone()

    if result:
        if token and token != result['token']:
            update_query = "UPDATE login SET token = %s WHERE device_id = %s"
            cursor.execute(update_query, (token, device_id))
            db.commit()
        return jsonify({'status': 'success', 'message': 'Device already logged in', 'userid': result['id']})
    else:
        insert_query = "INSERT INTO login (device_id, token) VALUES (%s, %s)"
        cursor.execute(insert_query, (device_id, token))
        db.commit()
        userid = cursor.lastrowid
        return jsonify({'status': 'success', 'message': 'New device registered', 'userid': userid})