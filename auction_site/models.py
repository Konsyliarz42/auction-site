from flask_sqlalchemy import SQLAlchemy
from flask_restx import fields
from flask_login import UserMixin

database = SQLAlchemy()

#================================================================
class Item(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)
    description = database.Column(database.String(2048))
    start_date = database.Column(database.Date(), nullable=False)
    end_date = database.Column(database.Date(), nullable=False)
    asking_price = database.Column(database.Float, default=0.00)
    current_price = database.Column(database.Float)

    owner_id = database.Column(database.Integer, database.ForeignKey('user.id'))
    winner_id = database.Column(database.Integer)

    def __str__(self):
        return f"Item: {self.name} ({self.current_price}zł)"


#================================================================
class User(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    nick = database.Column(database.String(256), nullable=False)
    first_name = database.Column(database.String(256))
    last_name = database.Column(database.String(256))
    active = database.Column(database.Boolean)
    admin = database.Column(database.Boolean)
    register_date = database.Column(database.Date(), nullable=False)
    password = database.Column(database.String(256), nullable=False)

    user_items = database.relationship('Item', backref='user')

    def __str__(self):
        return f"User: {self.nick} ({self.first_name} {self.last_name})"