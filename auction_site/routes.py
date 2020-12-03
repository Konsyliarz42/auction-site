from datetime import date
from flask import jsonify, request, render_template, make_response, redirect, url_for
from flask_restx import Api, Resource
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from .models import Item, User
from .models import database
from .forms import LoginForm, RegisterForm, NewPriceForm, EditUserForm, AddItemForm, EditItemForm

api = Api()

#================================================================
@api.route('/home')
class Home(Resource):

    @api.response(200, 'Success - Homepage is loaded')
    def get(self):
        user = None

        if current_user.is_authenticated:
            user = current_user

        return make_response(render_template('base.html', user=user), 200)


    @api.response(303, 'See Other - Correct logout')
    def post(self):
        current_user.active = False
        database.session.add(current_user)
        database.session.commit()
        logout_user()
        return redirect('home', 303)
   

@api.route('/register')
class Register(Resource):

    @api.response(200, 'Success - Correct load form')
    def get(self):
        form = RegisterForm()
        return make_response(render_template('register.html', form=form), 200)


    @api.response(303, 'See Other - User is add to database')
    @api.response(400, 'Bad request - Incorrect form value')
    @api.expect(api.model('User', User.FIELDS))
    def post(self):
        form = RegisterForm()
        
        if form.validate_on_submit():
            user = User(
                nick = form.nick.data,
                first_name = form.first_name.data,
                last_name = form.last_name.data,
                password = generate_password_hash(form.password.data, 'sha256'),
                register_date = date.today(),
                active = True,
                admin = False,
                user_items = []
            )

            if user.nick in [u.nick for u in User.query.all()]:
                return make_response(render_template('register.html', form=form), 400)

            database.session.add(user)
            database.session.commit()

            return redirect('home', 303)


@api.route('/login')
class Login(Resource):

    @api.response(200, 'Success - Correct load form')
    def get(self):
        form = LoginForm()
        return make_response(render_template('login.html', form=form), 200)


    @api.response(400, 'Bad request - Incorrect form value')
    @api.response(303, 'See Other - Correct login')
    def post(self):

        form = LoginForm()
        
        if form.validate_on_submit():
            user = User.query.filter_by(nick=form.nick.data).first()

            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                user.active = True
                database.session.add(user)
                database.session.commit()
                return redirect('home', 303)

        return make_response(render_template('login.html', form=form), 400)


#================================================================
@api.route('/users')
class UsersAll(Resource):

    @api.response(200, 'Success - List of users is loaded')
    def get(self):
        users = User.query.all()
        user = None

        if current_user.is_authenticated:
            user = current_user

        return make_response(render_template('users.html', user=user, users=users, User=User), 200)


@api.route('/user/<int:user_id>')
class UserOne(Resource):

    @api.response(401, 'Unauthorized — Login required')
    @api.response(200, 'Success - User is loaded')
    @login_required
    def get(self, user_id):
        user = current_user
        form = EditUserForm()
        form.nick.default = user.nick
        form.first_name.default = user.first_name
        form.last_name.default = user.last_name
        form.process()

        return make_response(render_template('user.html', user=user, form=form), 200)


    @api.response(401, 'Unauthorized — Login required')
    @api.response(303, 'See Other - Correct form')
    @api.expect(api.model('User', User.FIELDS))
    @login_required
    def post(self, user_id):
        user = current_user
        form = EditUserForm()

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
                for item in user.user_items:
                    database.session.delete(item)
                    
                database.session.delete(user)
                database.session.commit()
                logout_user()
                return redirect(url_for('home'), 303)

        return make_response(render_template('user.html', user=user, form=form), 200)


#================================================================
@api.route('/items')
class ItemsAll(Resource):

    @api.response(200, 'Success - List of items is loaded')
    def get(self):
        items = Item.query.all()
        user = None
        today_date = date.today()

        if current_user.is_authenticated:
            user = current_user

        return make_response(render_template('items.html', user=user, items=items, User=User, today_date=today_date), 200)


@api.route('/item/<int:item_id>')
class ItemOne(Resource):

    @api.response(200, 'Success - Item is loaded')
    def get(self, item_id):
        item = Item.query.get(item_id)
        user = None
        today_date = date.today()
        form = NewPriceForm()

        if current_user.is_authenticated:
            user = current_user

        if item:
            return make_response(render_template('item.html', user=user, item=item, User=User, today_date=today_date, form=form), 200)


    @api.response(401, 'Unauthorized — Login required')
    @api.response(200, 'Success - Correct change price')
    @login_required
    def post(self, item_id):
        form = NewPriceForm()
        
        if form.validate_on_submit():
            item = Item.query.get(item_id)
            user = current_user
            today_date = date.today()

            if item.current_price < form.new_price.data:
                item.current_price = form.new_price.data
                item.winner_id = user.id

                database.session.add(item)
                database.session.commit()
        
            return make_response(render_template('item.html', user=user, item=item, User=User, today_date=today_date, form=form), 200)


@api.route('/items/add')
class ItemAdd(Resource):

    @api.response(401, 'Unauthorized — Login required')
    @api.response(200, 'Success - Form is loaded')
    @login_required
    def get(self):
        user = current_user
        form = AddItemForm()
        
        return make_response(render_template('add_item.html', user=user, form=form), 200)


    @api.response(401, 'Unauthorized — Login required')
    @api.response(303, 'See Other - Item is add to database')
    @api.response(400, 'Bad request - Incorrect form value')
    @api.expect(api.model('Item', Item.FIELDS))
    @login_required
    def post(self):
        user = current_user
        form = AddItemForm()

        if form.validate_on_submit():
            item = Item(
                name = form.name.data,
                description = form.description.data,
                asking_price = form.asking_price.data,
                current_price = form.asking_price.data,
                start_date = form.start_date.data,
                end_date = form.end_date.data,
                owner_id = user.id
            )

            if item.start_date > item.end_date:
                return make_response(render_template('add_item.html', user=user, form=form), 400)

            if item.start_date < date.today():
                return make_response(render_template('add_item.html', user=user, form=form), 400)

            database.session.add(item)
            database.session.commit()
        
        return redirect(url_for('items_all'), 303)


@api.route('/item/edit/<int:item_id>')
class ItemEdit(Resource):

    @api.response(401, 'Unauthorized — Login required')
    @api.response(200, 'Success - Form is loaded')
    @login_required
    def get(self, item_id):
        user = current_user
        item = Item.query.get(item_id)
        today_date = date.today()

        form = AddItemForm()
        form.name.default = item.name
        form.description.default = item.description
        form.start_date.default = item.start_date
        form.end_date.default = item.end_date
        form.process()
        
        return make_response(render_template('edit_item.html', user=user, item=item, today_date=today_date, form=form), 200)


    @api.response(401, 'Unauthorized — Login required')
    @api.response(400, 'Bad request - Incorrect form value')
    @api.response(303, 'See Other - Correct form')
    @api.expect(api.model('Item', Item.FIELDS))
    @login_required
    def post(self, item_id):
    
        user = current_user
        item = Item.query.get(item_id)
        form = EditItemForm()

        if form.validate_on_submit():
            item.name = form.name.data
            item.description = form.description.data
            item.asking_price = form.asking_price.data
            item.current_price = form.asking_price.data
            item.start_date = form.start_date.data
            item.end_date = form.end_date.data

            if item.start_date > item.end_date:
                return make_response(render_template('edit_item.html', user=user, form=form), 400)

            if item.start_date < date.today():
                return make_response(render_template('edit_item.html', user=user, form=form), 400)

            database.session.add(item)
            database.session.commit()
        
        return redirect(url_for("user_one", user_id=user.id), 303)
