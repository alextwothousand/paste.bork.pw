from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    email = db.Column(db.String(100))

class Paste(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer)
    sha = db.Column(db.String(60))
    type = db.Column(db.Integer, default='0')
    info = db.Column(db.String(20))
    moreinfo = db.Column(db.String(50), default='')
    code = db.Column(db.String(5000))