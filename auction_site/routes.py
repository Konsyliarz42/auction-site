from datetime import datetime
from flask_restx import Api, Resource
from flask import jsonify, request

from .models import Item
from .models import database
from .functions import value_form

DATETIME = "%d.%m.%Y"

api = Api()

@api.route('/items')
class ItemsAll(Resource):

    def get(self):
        items = Item.query.all()
        items_list = list()

        for item in items:
            items_list.append({
                'id': item.id, 'name': item.name, 'descrition': item.description,
                'start_date': item.start_date.strftime(DATETIME), 'end_date': item.end_date.strftime(DATETIME),
                'first_price': item.first_price, 'last_price': item.last_price,
                '_links': {'self': request.url_root + f'item/{item.id}'}
            })

        return jsonify(items_list)


    def post(self):
        form = request.get_json()
        item = Item(
            name = value_form(form, 'name'),
            description = value_form(form, 'description'),
            first_price = value_form(form, 'first_price'),
            start_date = datetime.strptime(
                value_form(form, 'start_date'), 
                DATETIME
            ),
            end_date = datetime.strptime(
                value_form(form, 'end_date'), 
                DATETIME
            )
        )

        if item.start_date > item.end_date:
            return {'error': "Start date is later than end date."}, 400

        item.last_price = item.first_price

        database.session.add(item)
        database.session.commit()

        return {'added': item.name}, 201


    def delete(self):
        items = Item.query.all()

        for item in items:
            database.session.delete(item)

        database.session.commit()

        return {'deleted': 'all items'}, 200


@api.route('/item/<int:id>')
class ItemOne(Resource):

    def get(self, id):
        item = Item.query.get(id)

        if item:
            return {
                'id': item.id, 'name': item.name, 'descrition': item.description,
                'start_date': item.start_date.strftime(DATETIME), 'end_date': item.end_date.strftime(DATETIME),
                'first_price': item.first_price, 'last_price': item.last_price,
                '_links': {'self': request.url_root + f'item/{item.id}'}
            }, 200

        return {'Error': 'Item is not find'}, 404


    def put(self, id):
        item = Item.query.get(id)

        if item:
            form = request.get_json()
            item_name = item.name

            item.name = value_form(form, 'name', item.name)
            item.description = value_form(form, 'description', item.description)
            item.last_price = value_form(form, 'last_price', item.last_price)
            item.start_date = datetime.strptime(
                value_form(form, 'start_date', item.start_date.strftime(DATETIME)),
                DATETIME
            )
            item.end_date = datetime.strptime(
                value_form(form, 'end_date', item.end_date.strftime(DATETIME)),
                DATETIME
            )

            if item.start_date > item.end_date:
                return {'error': "Start date is later than end date."}, 400

            database.session.add(item)
            database.session.commit()

            return {'modified': item_name}, 200

        return {'Error': 'Item is not find'}, 404

    
    def patch(self, id):
        item = Item.query.get(id)

        if item:
            form = request.get_json()
            value = value_form(form, 'last_price', item.last_price)

            if value <= item.last_price:
                return {'Error': 'Your price is lower'}, 400
            else:
                item.last_price = value

            database.session.add(item)
            database.session.commit()

            return {'price is updated': item.name}, 200

        return {'Error': 'Item is not find'}, 404


    def delete(self, id):
        item = Item.query.get(id)

        if item:
            item_name = item.name

            database.session.delete(item)
            database.session.commit()

            return {'deleted': item.name}, 200

        return {'Error': 'Item is not find'}, 404