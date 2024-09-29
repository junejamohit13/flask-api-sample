from database import db

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    employee = db.relationship('Employee', backref='department', uselist=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
