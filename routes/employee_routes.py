from flask import Blueprint, jsonify, request
from database import db
from models.employee import Employee
from flask import current_app
employee_bp = Blueprint('employee_bp', __name__)

@employee_bp.route('/employees', methods=['GET'])
def get_employees():
    
    return current_app.employee_cache

@employee_bp.route('/employee/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    return current_app.employee_cache.get(employee_id,{})

@employee_bp.route('/employee/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    data = request.json
    employee = current_app.employee_cache.get(employee_id)
    if employee:
        employee.name = data.get('name', employee.name)
        employee.department_id = data.get('department_id', employee.department_id)
        db.session.commit()
        update_cache(current_app.employee_cache, employee_id, employee)
        return jsonify({'message': 'Employee updated'})
    return jsonify({'error': 'Employee not found'}), 404
