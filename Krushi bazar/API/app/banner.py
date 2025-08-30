from flask import Blueprint, jsonify
from API.db_connect import get_db

banner_bp = Blueprint('banner', __name__)

@banner_bp.route('/API/banner', methods=['GET'])
def banner():
    db = get_db()
    cursor = db.cursor()
    query = "SELECT id, description, title FROM banner"
    cursor.execute(query)
    banners = cursor.fetchall()  # DictCursor automatically returns dictionaries
    if banners:
        return jsonify({'status': 'success', 'data': banners})
    else:
        return jsonify({'status': 'error', 'message': 'No banners found'})