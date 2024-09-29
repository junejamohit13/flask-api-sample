from flask import Blueprint, jsonify, request
from database import db
from models.location import Location
from flask import current_app
location_bp = Blueprint('location_bp', __name__)

@location_bp.route('/locations', methods=['GET'])
def get_locations():
    return jsonify([{
        'id': loc.id,
        'name': loc.name
    } for loc in current_app.location_cache.values()])

@location_bp.route('/location/<int:location_id>', methods=['GET'])
def get_location(location_id):
    location = current_app.location_cache.get(location_id)
    if location:
        return jsonify({
            'id': location.id,
            'name': location.name
        })
    return jsonify({'error': 'Location not found'}), 404

@location_bp.route('/location/<int:location_id>', methods=['PUT'])
def update_location(location_id):
    data = request.json
    location = current_app.location_cache.get(location_id)
    if location:
        location.name = data.get('name', location.name)
        db.session.commit()
        update_cache(location_cache, location_id, location)
        return jsonify({'message': 'Location updated'})
    return jsonify({'error': 'Location not found'}), 404
