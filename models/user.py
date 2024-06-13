from database import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(80), nullable=False, default='user')

    def to_dict(user):
        if user:
            return {
                "id": user.id,
                "username": user.username,
                "password": user.password,
                "role": user.role
            }
        
        return None