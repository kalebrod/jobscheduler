from datetime import datetime
from .extensions import db

class Jobs(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20))
    task = db.Column(db.String(30))
    status = db.Column(db.String(15))
    start = db.Column(db.DateTime,default=datetime.now())
    # active = db.Column(db.String(20))

    def __repr__(self):
        return '<Job {} - {}>'.format(self.id,self.name)