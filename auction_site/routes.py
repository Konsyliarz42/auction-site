from datetime import datetime
from flask import jsonify, request, render_template, make_response, redirect, url_for
from flask_restx import Api, Resource
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from .models import Item, User
from .models import database
from .functions import value_form
from .forms import LoginForm, RegisterForm, NewPriceForm, EditUser


DATETIME = "%d.%m.%Y"

api = Api()

@api.route('/home')
class Home(Resource):

    def get(self):
        user = None

        if current_user.is_authenticated:
            user = current_user

        return make_response(render_template('base.html', user=user), 200)

    
    def post(self):
        current_user.active = False
        database.session.add(current_user)
        database.session.commit()
        logout_user()
        return redirect('home', 200)
   

@api.route('/register')
class Register(Resource):

    def get(self):
        form = RegisterForm()
        return make_response(render_template('register.html', form=form), 200)


    def post(self):
        form = RegisterForm()
        
        if form.validate_on_submit():
            user = User(
                nick = form.nick.data,
                first_name = form.first_name.data,
                last_name = form.last_name.data,
                password = generate_password_hash(form.password.data, 'sha256'),
                register_date = datetime.now(),
                active = True,
                admin = False,
                user_items = []
            )

            if user.nick in [u.nick for u in User.query.all()]:
                return make_response(render_template('register.html', form=form), 400)

            database.session.add(user)
            database.session.commit()

            return redirect('home', 200)

@api.route('/login')
class Login(Resource):

    def get(self):
        form = LoginForm()
        return make_response(render_template('login.html', form=form), 200)


    def post(self):

        form = LoginForm()
        
        if form.validate_on_submit():
            user = User.query.filter_by(nick=form.nick.data).first()

            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                user.active = True
                database.session.add(user)
                database.session.commit()
                return redirect('home', 200)

        return make_response(render_template('login.html', form=form), 400)


@api.route('/items')
class ItemsAll(Resource):

    def get(self):
        items = Item.query.all()
        user = None
        today_date = datetime.today().date()

        if current_user.is_authenticated:
            user = current_user

        return make_response(render_template('items.html', user=user, items=items, User=User, today_date=today_date), 200)


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
            owner_id = 1
        )

        if item.start_date > item.end_date:
            return {'error': "Start date is later than end date."}, 400

        if item.start_date.date() < datetime.today().date():
            return {'error': "Start date can't be earlier than today date."}, 400

        database.session.add(item)
        database.session.commit()

        return {'added': item.name}, 201

@api.route('/item/<int:item_id>')
class ItemOne(Resource):

    def get(self, item_id):
        item = Item.query.get(item_id)
        user = None
        today_date = datetime.today().date()
        form = NewPriceForm()

        if current_user.is_authenticated:
            user = current_user

        if item:
            return make_response(render_template('item.html', user=user, item=item, User=User, today_date=today_date, form=form), 200)


    @login_required
    def post(self, item_id):
        form = NewPriceForm()
        
        if form.validate_on_submit():
            item = Item.query.get(item_id)
            user = current_user
            today_date = datetime.today().date()

            if item.current_price < form.new_price.data:
                item.current_price = form.new_price.data
                item.winner_id = user.id

                database.session.add(item)
                database.session.commit()
        
            return make_response(render_template('item.html', user=user, item=item, User=User, today_date=today_date, form=form), 200)


@api.route('/users')
class UsersAll(Resource):

    def get(self):
        users = User.query.all()
        user = None

        if current_user.is_authenticated:
            user = current_user

        return make_response(render_template('users.html', user=user, users=users, User=User), 200)


@api.route('/user/<int:user_id>')
class UserOne(Resource):

    @login_required
    def get(self, user_id):
        user = current_user
        form = EditUser()
        form.nick.default = user.nick
        form.first_name.default = user.first_name
        form.last_name.default = user.last_name
        form.process()

        return make_response(render_template('user.html', user=user, form=form), 200)


    @login_required
    def post(self, user_id):
        user = current_user
        form = EditUser(user=user)

        if form.validate_on_submit():
            user.nick = form.nick.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data

            if request.form.get('new_password') and check_password_hash(user.password, request.form.get('old_password')):
                user.password = generate_password_hash(request.form.get('new_password'), 'sha256')

            for item in user.user_items:
                if request.form.get('delitem' + str(item.id)):
                    user.user_items.remove(item)
                    database.session.delete(item)
                
            database.session.add(user)
            database.session.commit()

            if request.form.get('deluser'):
                database.session.delete(user)
                database.session.commit()
                logout_user()
                return redirect(api.url_for('home'), 200)

        return make_response(render_template('user.html', user=user, form=form), 200)