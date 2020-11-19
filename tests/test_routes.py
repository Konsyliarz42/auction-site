from faker import Faker
from random import random, randint
from datetime import datetime, timedelta
from flask import Flask
from flask_testing import TestCase

from . import app, database, DATETIME

def create_items(quantity=1):
    """Returns list of random items."""

    fake = Faker()
    items = list()

    for _ in range(quantity):
        d = randint(0, 11)
        date1 = datetime.today()
        date2 = date1 + timedelta(days=d)

        items.append({
            "name": fake.company(),
            "start_date": date1.strftime(DATETIME),
            "end_date": date2.strftime(DATETIME),
            "asking_price": round(random(), 2)
        })

    if quantity == 1:
        items = items[0]

    return items


def create_users(quantity=1):
    """Returns list of random users."""

    fake = Faker()
    users = list()

    for _ in range(quantity):
        users.append({
            'nick': fake.name(),
            'password': fake.password()
        })

    if quantity == 1:
        users = users[0]

    return users

#================================================================

class TestRoutes(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        return app

    
    def setUp(self):
        database.create_all()

        user = {
            'nick': 'tester',
            'register_date': Faker().date_object().strftime(DATETIME),
            'password': 'test'
        }
        self.client.post("/users", json=user)
        self.client.post("/login", json={'nick': user['nick'], 'password': user['password']})


    def tearDown(self):
        database.session.remove()
        database.drop_all()

#================================================================
    
    # Get all items form database
    def test_get_items(self):
        response = self.client.get("/items")
        self.assertEqual(response.status_code, 200)


    # Add new item to database
    def test_post_items(self):
        item = create_items()
        response = self.client.post("/items", json=item)
        self.assertEqual(response.status_code, 201)


    # Add new item when start date is later than end date
    def test_post_items_late_start_date(self):
        item = create_items()
        date = datetime.today().date()
        item['start_date'] = (date + timedelta(3)).strftime(DATETIME)
        item['end_date'] = date.strftime(DATETIME)

        response = self.client.post("/items", json=item)
        self.assertEqual(response.status_code, 400)


    # Add new item when start date is earlier than today date
    def test_post_items_earlier_start_date(self):
        item = create_items()
        date = datetime.today().date()
        item['start_date'] = (date - timedelta(3)).strftime(DATETIME)

        response = self.client.post("/items", json=item)
        self.assertEqual(response.status_code, 400)


    # Delete all items
    def test_delete_items(self):
        response = self.client.delete("/items")
        self.assertEqual(response.status_code, 200)

    #-------------------------------- 

    # Get item by id
    def test_get_item(self):
        item = create_items()
        self.client.post("/items", json=item)

        response = self.client.get("/item/1")
        self.assertEqual(response.status_code, 200)


    # Get item by id when database is empty
    def test_get_item_empty_database(self):
        response = self.client.get("/item/1")
        self.assertEqual(response.status_code, 404)


    # Modifide item 
    def test_put_item(self):
        item = create_items()
        self.client.post("/items", json=item)
        start_date = datetime.strptime(item['start_date'], DATETIME)
        end_date = start_date + timedelta(days=randint(0, 11))

        item = create_items()
        item.pop('start_date')
        item['end_date'] = end_date.strftime(DATETIME)
        response = self.client.put("/item/1", json=item)
        self.assertEqual(response.status_code, 200)

    
    # Modifide item when database is empty
    def test_put_item_empty_database(self):
        item = create_items()
        response = self.client.put("/item/1", json=item)
        self.assertEqual(response.status_code, 404)


    # Rise item's price
    def test_patch_item(self):
        item = create_items()
        self.client.post("/items", json=item)

        item = {"current_price": item['asking_price'] + randint(1, 10)}
        response = self.client.patch("/item/1", json=item)
        self.assertEqual(response.status_code, 200)

    
    # Rise item's price lower values
    def test_patch_item(self):
        item = create_items()
        self.client.post("/items", json=item)

        item = {"current_price": item['asking_price'] - randint(1, 10)}
        response = self.client.patch("/item/1", json=item)
        self.assertEqual(response.status_code, 400)


    # Rise item's price when database is empty
    def test_patch_item_empty_database(self):
        item = {"current_price": randint(1, 10)}
        response = self.client.patch("/item/1", json=item)
        self.assertEqual(response.status_code, 404)


    # Delete item
    def test_delete_item(self):
        item = create_items()
        self.client.post("/items", json=item)

        response = self.client.delete("/item/1")
        self.assertEqual(response.status_code, 200)
        

    # Delete item when database is empty
    def test_delete_item_empty_database(self):
        response = self.client.delete("/item/1")
        self.assertEqual(response.status_code, 404)

#================================================================

    # Get all users form database
    def test_get_users(self):
        response = self.client.get("/users")
        self.assertEqual(response.status_code, 200)


    # Add new user to database
    def test_post_users(self):
        user = create_users()
        response = self.client.post("/users", json=user)
        self.assertEqual(response.status_code, 201)


    # Add new user when user's nick is already in database
    def test_post_users_nick_exist(self):
        user = create_users()
        user_nick = user['nick']
        self.client.post("/users", json=user)

        user = create_users()
        user['nick'] = user_nick
        response = self.client.post("/users", json=user)
        self.assertEqual(response.status_code, 400)


    # Delete all users from database
    def test_delete_users(self):
        response = self.client.delete("/users")
        self.assertEqual(response.status_code, 200)

    #--------------------------------

    # Get test user by id
    def test_get_user(self):
        # Test user is added to database before start tests
        response = self.client.get("/user/1")
        self.assertEqual(response.status_code, 200)


    # Get user by id when database is empty
    def test_get_user_empty_database(self):
        self.client.delete("/users")

        response = self.client.get("/user/1")
        self.assertEqual(response.status_code, 404)


    # Modifide test user
    def test_put_user(self):
        user = create_users()
        response = self.client.put("/user/1", json=user)
        self.assertEqual(response.status_code, 200)


    # Modifide test user when database is empty
    def test_put_user_empty_database(self):
        self.client.delete("/users")

        user = create_users()
        response = self.client.put("/user/1", json=user)
        self.assertEqual(response.status_code, 401)


    # Modifide user if user is not find
    def test_put_user_not_find(self):
        user = create_users()
        response = self.client.put("/user/2", json=user)
        self.assertEqual(response.status_code, 404)


    # Modifide user when new user's nick is already in database
    def test_put_user_nick_exist(self):
        user = create_users()
        user_nick = user['nick']
        self.client.post("/users", json=user)

        user = create_users()
        user['nick'] = user_nick
        response = self.client.put("/user/1", json=user)
        self.assertEqual(response.status_code, 400)


    # Change user's list of items
    def test_patch_user(self):
        for item in create_items(3):
            self.client.post("/items", json=item)

        items = {'user_items': [1, 2, 3]}
        response = self.client.patch("/user/1", json=items)
        self.assertEqual(response.status_code, 200)


    # Change user's list of items when item is not in database
    def test_patch_user_item_not_exist(self):
        items = {'user_items': [1]}
        response = self.client.patch("/user/1", json=items)
        self.assertEqual(response.status_code, 400)

    
    # Delete user from database
    def test_delete_user(self):
        response = self.client.delete("/user/1")
        self.assertEqual(response.status_code, 200)

    
    # Delete user when user is not in database
    def test_delete_user_not_exists(self):
        response = self.client.delete("/user/2")
        self.assertEqual(response.status_code, 404)