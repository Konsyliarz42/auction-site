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
        days = randint(0, 11)
        date1 = fake.date_object()
        date2 = date1 + timedelta(days)

        items.append({
            "name": fake.company(),
            "start_date": date1.strftime(DATETIME),
            "end_date": date2.strftime(DATETIME),
            "first_price": round(random(), 2)
        })

    if quantity == 1:
        items = items[0]

    return items

#================================================================

class TestRoutes(TestCase):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

    def create_app(self):
        return app

    
    def setUp(self):
        database.create_all()


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
        date = Faker().date_object()
        item['start_date'] = (date + timedelta(3)).strftime(DATETIME)
        item['end_date'] = date.strftime(DATETIME)

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

        item = create_items()
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

        item = {"last_price": item['first_price'] + randint(1, 10)}
        response = self.client.patch("/item/1", json=item)
        self.assertEqual(response.status_code, 200)

    
    # Rise item's price lower values
    def test_patch_item(self):
        item = create_items()
        self.client.post("/items", json=item)

        item = {"last_price": item['first_price'] - randint(1, 10)}
        response = self.client.patch("/item/1", json=item)
        self.assertEqual(response.status_code, 400)

    # Rise item's price when database is empty
    def test_patch_item_empty_database(self):
        item = {"last_price": randint(1, 10)}
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

#--------------------------------
