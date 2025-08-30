from flask import Blueprint, request, jsonify
from API.db_connect import get_db

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/API/alerts', methods=['POST'])
def alerts():
    db = get_db()
    data = request.get_json()

    action = data.get('action', '').strip()
    userid = data.get('userid')
    marketid = data.get('marketid')
    commodity = data.get('commodity')
    variety = data.get('variety')

    cursor = db.cursor()

    if not action:
        return jsonify({'status': 'error', 'message': 'Action is required'})

    if action == 'add':
        if not all([userid, marketid, commodity, data.get('conditions'), data.get('amount')]):
            return jsonify({'status': 'error', 'message': 'All fields are required for add'})
        conditions = data.get('conditions')
        amount = data.get('amount')
        insert_query = """
            INSERT INTO alerts (userid, marketid, commodity, variety, conditions, amount)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (userid, marketid, commodity, variety, conditions, amount))
        db.commit()
        return jsonify({'status': 'success', 'message': 'Condition added'})

    elif action == 'delete':
        alert_id = int(data.get('id', 0))
        if alert_id <= 0:
            return jsonify({'status': 'error', 'message': 'id is required for delete'})
        delete_query = "DELETE FROM alerts WHERE id = %s"
        cursor.execute(delete_query, (alert_id,))
        db.commit()
        if cursor.rowcount > 0:
            return jsonify({'status': 'success', 'message': 'Condition deleted'})
        else:
            return jsonify({'status': 'error', 'message': 'No record found with given id'})

    elif action == 'get':
        if not userid:
            return jsonify({'status': 'error', 'message': 'userid is required for get'})
        get_query = """
            SELECT a.*, m.name AS market_name
            FROM alerts a
            LEFT JOIN markets m ON a.marketid = m.id
            WHERE a.userid = %s
        """
        cursor.execute(get_query, (userid,))
        data = cursor.fetchall()  # DictCursor automatically returns dictionaries
        return jsonify({'status': 'success', 'data': data})

    else:
        return jsonify({'status': 'error', 'message': 'Invalid action'})