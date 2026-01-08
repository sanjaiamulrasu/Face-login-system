from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))
    roll_no = db.Column(db.String(20))
    department = db.Column(db.String(50))
    dob = db.Column(db.Date)
    phone = db.Column(db.String(15))
    email = db.Column(db.String(100))
    face_encoding = db.Column(db.LargeBinary)