from flask import Blueprint, jsonify, request
from database import db
from models.department import Department
from flask import current_app
department_bp = Blueprint('department_bp', __name__)

@department_bp.route('/departments', methods=['GET'])
def get_departments():
    return current_app.department_cache

@department_bp.route('/department/<int:department_id>', methods=['GET'])
def get_department(department_id):
    return current_app.deparment_cache.get(department_id,{})
@department_bp.route('/department/<int:department_id>', methods=['PUT'])
def update_department(department_id):
    data = request.json
    department = department_cache.get(department_id)
    if department:
        department.name = data.get('name', department.name)
        department.location_id = data.get('location_id', department.location_id)
        db.session.commit()
        update_cache(current_app.department_cache, department_id, department)
        return jsonify({'message': 'Department updated'})
    return jsonify({'error': 'Department not found'}), 404
