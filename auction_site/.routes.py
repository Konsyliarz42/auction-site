from datetime import datetime
from flask import jsonify, request, render_template, make_response, flash
from flask_restx import Api, Resource
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from .models import Item, User
from .models import database
from .functions import value_form

DATETIME = "%d.%m.%Y"

api = Api()

#==============================================================

@api.route('/login')
class LoginUser(Resource):

    def get(self):
        return make_response(render_template('base.html'), 200)


    def post(self):
        form = request.get_json()
        user = User.query.filter_by(nick=request.form.get("nick")).first()

        if user and check_password_hash(user.password, request.form.get("password")):
            login_user(user)
            user.active = True
            database.session.add(user)
            database.session.commit()

            flash("{'login': user.nick}")

        return {'error': "Bad nick or password"}

    
    def patch(self):
        nick = current_user.nick
        current_user.active = False
        database.session.add(current_user)
        database.session.commit()
        logout_user()

        return {'logout': nick}, 200


#==============================================================

@api.route('/items')
class ItemsAll(Resource):

    def get(self):
        items = Item.query.all()
        items_list = list()

        for item in items:
            owner = User.query.get(item.owner_id)
            owner = {'id': owner.id, 'nick': owner.nick}

            items_list.append({
                'id': item.id, 'name': item.name, 'descrition': item.description,
                'start_date': item.start_date.strftime(DATETIME), 'end_date': item.end_date.strftime(DATETIME),
                'asking_price': item.asking_price, 'current_price': item.current_price,
                'owner': owner, 
                '_links': {
                    'self': request.url_root + f'item/{item.id}',
                    'owner': request.url_root + f"user/{owner['id']}"
                }
            })

        return jsonify(items_list)


    @login_required
    def post(self):
        form = request.get_json()
        item = Item(
            name = value_form(form, 'name'),
            description = value_form(form, 'description'),
            asking_price = value_form(form, 'asking_price'),
            current_price = value_form(form, 'asking_price'),
            start_date = datetime.strptime(
                value_form(form, 'start_date'), 
                DATETIME
            ),
            end_date = datetime.strptime(
                value_form(form, 'end_date'), 
                DATETIME
            ),
            owner_id = current_user.id
        )

        if item.start_date > item.end_date:
            return {'error': "Start date is later than end date."}, 400

        if item.start_date.date() < datetime.today().date():
            return {'error': "Start date can't be earlier than today date."}, 400

        database.session.add(item)
        database.session.commit()

        return {'added': item.name}, 201


    @login_required
    def delete(self):
        if current_user.admin ==  False:
            return {'error': "You have not permissions to deletes"}, 401

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
            owner = User.query.get(item.owner_id)
            owner = {'id': owner.id, 'nick': owner.nick}

            return {
                'id': item.id, 'name': item.name, 'descrition': item.description,
                'start_date': item.start_date.strftime(DATETIME), 'end_date': item.end_date.strftime(DATETIME),
                'asking_price': item.asking_price, 'current_price': item.current_price,
                'owner': owner, 
                '_links': {
                    'self': request.url_root + f'item/{item.id}',
                    'owner': request.url_root + f"user/{owner['id']}"
                }
            }, 200

        return {'Error': 'Item is not find'}, 404


    @login_required
    def put(self, id):
        item = Item.query.get(id)

        if item:
            if item.owner_id != current_user.id and current_user.admin == False:
                return {'Error': 'Item is not yours'}, 401

            form = request.get_json()
            item_name = item.name

            item.name = value_form(form, 'name', item.name)
            item.description = value_form(form, 'description', item.description)
            item.current_price = value_form(form, 'current_price', item.current_price)
            item.end_date = datetime.strptime(
                value_form(form, 'end_date', item.end_date.strftime(DATETIME)),
                DATETIME
            ).date()

            if item.start_date > item.end_date:
                return {'error': "Start date is later than end date."}, 400

            database.session.add(item)
            database.session.commit()

            return {'modified': item_name}, 200

        return {'Error': 'Item is not find'}, 404


    @login_required
    def patch(self, id):
        item = Item.query.get(id)

        if item:
            form = request.get_json()
            value = value_form(form, 'current_price', item.current_price)

            if value <= item.current_price:
                return {'Error': 'Your price is lower'}, 400
            else:
                item.current_price = value

            database.session.add(item)
            database.session.commit()

            return {'price is updated': item.name}, 200

        return {'Error': 'Item is not find'}, 404


    @login_required
    def delete(self, id):
        item = Item.query.get(id)

        if item:
            if item.owner_id != current_user.id and current_user.admin == False:
                return {'Error': 'Item is not yours'}, 401

            database.session.delete(item)
            database.session.commit()

            return {'deleted': item.name}, 200

        return {'Error': 'Item is not find'}, 404

#==============================================================

@api.route('/users')
class UsersAll(Resource):

    def get(self):
        users = User.query.all()
        users_list = list()

        for user in users:
            items = [{'name': i.name, 'id': i.id} for i in user.user_items]

            users_list.append({
                'id': user.id, 'nick': user.nick,
                'first_name': user.first_name, 'last_name': user.last_name,
                'active': user.active, 'admin': user.admin, 'register_date': user.register_date.strftime(DATETIME),
                'user_items': items,'_links': {'self': request.url_root + f'user/{user.id}'}
            })

            for item in items:
                users_list[-1]['_links'][item['name']] = request.url_root + f"item/{item['id']}"

        return jsonify(users_list)


    def post(self):
        form = request.get_json()
        user = User(
            nick = value_form(form, 'nick'),
            first_name = value_form(form, 'first_name'),
            last_name = value_form(form, 'last_name'),
            password = generate_password_hash(value_form(form, 'password'), 'sha256'),
            register_date = datetime.now(),
            active = True,
            admin = False,
            user_items = []
        )

        if user.nick in [u.nick for u in User.query.all()]:
            return {'error': f"{user.nick} is already in database"}, 400

        database.session.add(user)
        database.session.commit()

        return {'added': f"{user.nick}"}, 201


    @login_required
    def delete(self):
        if current_user.admin ==  False:
            return {'error': "You have not permissions to deletes"}, 401
            
        users = User.query.all()

        for user in users:
            database.session.delete(user)

        database.session.commit()
        logout_user()

        return {'deleted': 'all users', 'info': "You are logout now"}, 200


@api.route('/user/<int:id>')
class UserOne(Resource):

    def get(self, id):
        user = User.query.get(id)

        if user:
            items = [{'name': i.name, 'id': i.id} for i in user.user_items]
            
            user =  {
                'id': user.id, 'nick': user.nick,
                'first_name': user.first_name, 'last_name': user.last_name,
                'active': user.active, 'admin': user.admin, 'register_date': user.register_date.strftime(DATETIME),
                'user_items': items, '_links': {'self': request.url_root + f'user/{user.id}'}
            }

            for item in items:
                user['_links'][item['name']] = request.url_root + f"item/{item['id']}"

            return user, 200

        return {'Error': 'User is not find'}, 404


    @login_required
    def put(self, id): 
        user = User.query.get(id)

        if user:
            if user.id != current_user.id and current_user.admin == False:
                return {'error': "You have not permissions to edit."}, 401

            form = request.get_json()
            user_name = user.nick
            users_nicks = [u.nick for u in User.query.all()]

            user.nick = value_form(form, 'nick', user.nick)
            user.first_name = value_form(form, 'first_name', user.first_name)
            user.last_name = value_form(form, 'last_name', user.last_name)
            user.password = generate_password_hash(value_form(form, 'password', user.password), 'sha256')

            if user.nick in users_nicks and user.nick != user_name:
                return {'error': f"{user.nick} is already in database"}, 400

            database.session.add(user)
            database.session.commit()

            return {'modifide': user_name}, 200

        return {'Error': 'User is not find'}, 404


    @login_required
    def patch(self, id):
        user = User.query.get(id)

        if user:
            if user.id != current_user.id and current_user.admin == False:
                return {'error': "You have not permissions to edit."}, 401

            form = request.get_json()
            items_ids = value_form(form, 'user_items')
            items = [i for i in Item.query.all() if i.id in items_ids]

            for item in items_ids:
                if not Item.query.get(item):
                    return {'Error': 'Item not found'}, 400

            user.user_items = items
            
            database.session.add(user)
            database.session.commit()

            return {'modifide': user.nick}, 200

        return {'Error': 'User is not find'}, 404


    @login_required
    def delete(self, id):
        user = User.query.get(id)

        if user:
            if user.id != current_user.id and current_user.admin == False:
                return {'error': "You can't delete other users"}, 401

            database.session.delete(user)
            database.session.commit()
            logout_user()

            return {'deleted': user.nick, 'info': "You are logout now"}, 200

        return {'error': 'User is not find'}, 404