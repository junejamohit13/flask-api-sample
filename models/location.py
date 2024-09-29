from database import db

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    departments = db.relationship('Department', backref='location', lazy=True)
