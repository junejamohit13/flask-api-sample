from models.employee import Employee
from models.department import Department
from models.location import Location
from database import db

def insert_sample_data():
    location1 = Location(name="New York")
    location2 = Location(name="San Francisco")

    department1 = Department(name="HR", location=location1)
    department2 = Department(name="Engineering", location=location2)

    employee1 = Employee(name="Alice", department=department1)
    employee2 = Employee(name="Bob", department=department2)

    db.session.add(location1)
    db.session.add(location2)
    db.session.add(department1)
    db.session.add(department2)
    db.session.add(employee1)
    db.session.add(employee2)
    db.session.commit()
