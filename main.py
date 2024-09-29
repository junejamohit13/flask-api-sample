from flask import Flask, current_app
from routes.employee_routes import employee_bp
from routes.department_routes import department_bp
from routes.location_routes import location_bp
from database import init_db
from cache import load_cache
from sample_data import insert_sample_data
from models.employee import Employee
from models.department import Department
from models.location import Location
app = Flask(__name__)

# Configure the database (SQLite for simplicity)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database and create tables
db = init_db(app)

# Register Blueprints
app.register_blueprint(employee_bp)
app.register_blueprint(department_bp)
app.register_blueprint(location_bp)

with app.app_context():
    insert_sample_data()
    print("Inserted sample data")
    load_cache(Employee, Department, Location, db)
    print("Loaded cache")
    print(current_app.employee_cache)
    

if __name__ == '__main__':
    app.run(debug=True)
