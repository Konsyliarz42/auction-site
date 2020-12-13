from datetime import date, timedelta
from random import randint, random
from flask import Flask
from flask_testing import TestCase
from flask_login import LoginManager, login_user, current_user
from werkzeug.security import generate_password_hash
from unittest.mock import patch, Mock

from . import app, database, User, Item
from . import LoginForm, RegisterForm, NewPriceForm, EditUserForm, AddItemForm, EditItemForm

def add_random_items():
    for i in range(randint(1, 21)):
        random_date = date.today() + timedelta(randint(0, 3))

        database.session.add(Item(
            name = f'Item{i}',
            description = 'Test item',
            asking_price = random(),
            start_date = random_date,
            end_date = random_date + timedelta(randint(0, 3)),
            owner_id = 1 
        ))

    database.session.commit()

#================================================================

class TestRoutes(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['LOGIN_DISABLED'] = True
        return app

    
    def setUp(self):
        database.create_all()

        database.session.add(User(
            nick = 'Tester',
            password = generate_password_hash('testPassword', 'sha256'),
            register_date = date.today(),
            admin = True,
            active = False,
            user_items = []
        ))
        database.session.commit()


    def tearDown(self):
        database.session.remove()
        database.drop_all()

#================================================================
    
    # Open home page
    def test_home_get(self):
        response = self.client.get("/home")
        self.assertEqual(response.status_code, 200)


    # Register user
    def test_register_post(self):
        form = RegisterForm()
        form.nick.default = 'TUser'
        form.password.default = 'password'
        form.process()

        response = self.client.post('/register', data=form.data)
        self.assertEqual(response.status_code, 303)


    # Login user
    def test_login_post(self):
        form = LoginForm()
        form.nick.default = 'Tester'
        form.password.default = 'testPassword'
        form.process()

        response = self.client.post('/login', data=form.data)
        self.assertEqual(response.status_code, 303)


    # Show items
    def test_items_get(self):
        add_random_items()

        response = self.client.get("/items")
        self.assertEqual(response.status_code, 200)


    # Show users
    def test_users_get(self):
        response = self.client.get("/users")
        self.assertEqual(response.status_code, 200)


    # Add item
    def test_add_item_post(self):
        form = AddItemForm()
        form.name.default = 'Item'
        form.description = 'Test item'
        form.process()

        with patch('auction_site.routes.current_user') as mock_user:
            mock_user.id = 1
            response = self.client.post("/items/add", data=form.data)
            self.assertEqual(response.status_code, 303)


    # Edit item
    def test_item_edit_post(self):
        add_random_items()

        form = EditItemForm()
        form.name.default = "Changed item"
        form.process()

        with patch('auction_site.routes.current_user') as mock_user:
            mock_user.id = 1
            response = self.client.post(f"/item/edit/{Item.query.first().id}", data=form.data)
            self.assertEqual(response.status_code, 303)


    # Edit user
    def test_user_post(self):
        form = EditUserForm()
        form.first_name.default = "First"
        form.process()

        with patch('auction_site.routes.current_user', new=User.query.first()):
            response = self.client.post(f"/user/{User.query.first().id}", data=form.data)
            self.assertEqual(response.status_code, 200)