# cache.py
from flask import current_app


def sqlalchemy_to_dict(obj,primary_key_column):
    result = {}
    for row in obj:
        row_dict = row.__dict__
        row_dict.pop( '_sa_instance_state', None)
        result[row_dict[primary_key_column]]=row_dict
    return result

def load_cache(Employee, Department, Location, db):
    employees = Employee.query.all()
    print(f"Employees: {employees}")

    # Initialize caches if they don't exist
    if not hasattr(current_app, 'employee_cache'):
        current_app.employee_cache = {}
    if not hasattr(current_app, 'department_cache'):
        current_app.department_cache = {}
    if not hasattr(current_app, 'location_cache'):
        current_app.location_cache = {}

    # Update the caches
    current_app.employee_cache.clear()

    
    current_app.employee_cache.update(sqlalchemy_to_dict(employees,'id'))

    departments = Department.query.all()
    current_app.department_cache.clear()
    current_app.department_cache.update(sqlalchemy_to_dict(departments,'id'))

    locations = Location.query.all()
    current_app.location_cache.clear()
    current_app.location_cache.update(sqlalchemy_to_dict(locations,'id'))

    print(f"Employee cache inside load_cache: {current_app.employee_cache}")


def update_cache(cache_name, key, obj):
    cache = getattr(current_app, cache_name)
    cache[key] = obj
