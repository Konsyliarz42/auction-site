from flask_sqlalchemy import SQLAlchemy
from flask_restx import fields

database = SQLAlchemy()

#================================================================
class Item(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)
    description = database.Column(database.String(2048))
    start_date = database.Column(database.Date(), nullable=False)
    end_date = database.Column(database.Date())
    first_price = database.Column(database.Float, nullable=False)
    last_price = database.Column(database.Float)
    #owner = database.Column(database.Integer, database.ForeignKey('user.id'))
    #buyer = database.Column(database.Integer, database.ForeignKey('user.id'))

    def __str__(self):
        return f"Item: {self.name} ({self.last_price}zł)"
