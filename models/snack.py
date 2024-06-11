from database import db

class Snack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    snackname = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    enjoyed_on = db.Column(db.DateTime(), nullable=False)

    def to_dict(snack):
        if snack:
            return {
                "id": snack.id,
                "snackname": snack.snackname,
                "description": snack.description,
                "enjoyed_on": snack.enjoyed_on
            }
        
        return None