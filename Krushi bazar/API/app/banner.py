from flask import Blueprint, jsonify
from API.db_connect import get_db

banner_bp = Blueprint('banner', __name__)

@banner_bp.route('/API/banner', methods=['POST'])
def banner():
    db = get_db()
    cursor = db.cursor()
    query = "SELECT id, description, title FROM banner"
    cursor.execute(query)
    banners = cursor.fetchall()  # DictCursor automatically returns dictionaries

    # Convert id to string for each banner
    for banner in banners:
        banner['id'] = str(banner['id'])

    if banners:
        return jsonify({'status': 'success', 'data': banners})
    else:
        return jsonify({'status': 'error', 'message': 'No banners found'})