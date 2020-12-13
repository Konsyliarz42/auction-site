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
        info = {
            'title': "Witaj na stronie głównej",
            'description': """Obecnie znajdujesz się na stronie głównej.
            Z tego miejsca możesz spokojnie przeglądać cały serwis.
            Przeglądać oferty, licytować bądź dodawać nowe oferty.
            W tym miejscu znajdziesz informację o stronach lub opcje do podstron serwisu."""
        }

        if current_user.is_authenticated:
            user = {
                'id': current_user.id,
                'nick': current_user.nick,
                'admin': current_user.admin
            }

        return make_response(render_template('base.html', user=user, info=info), 200)


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
        user = None
        info = {
            'title': "Rejestracja",
            'description': """Do zarejestrowania w serwisie wystarczą tylko podstawowe informacje."""
        }
        return make_response(render_template('register.html', user=user, info=info, form=form), 200)


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
        user = None
        info = {
            'title': "Logowanie",
            'description': """Zalogować się możesz wyłącznie jeśli posiadasz już konto.
            Jeżeli jeszcze go nie masz wystarczy że klikniesz 'Zarejestruj się' i wypełnisz krótki formularz.
            Będąc zalogowanym w tym panelu znajdziesz również przyciski do zaządzania profilem."""
        }
        return make_response(render_template('login.html', user=user, info=info, form=form), 200)


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
        info = {
            'title': "Lista użytkowników",
            'description': """Znajdziesz tutaj karty wszystkich użytkowników zarejestrowanych w serwisie."""
        }

        if current_user.is_authenticated:
            user = current_user

        return make_response(render_template('users.html', user=user, info=info, users=users, User=User), 200)


@api.route('/user/<int:user_id>')
class UserOne(Resource):

    @api.response(401, 'Unauthorized — Login required')
    @api.response(200, 'Success - User is loaded')
    @login_required
    def get(self, user_id):
        user = current_user
        info = {
            'title': "Strona twojego profilu",
            'description': """Znajdziesz tutaj wszytkie informacje o swoim profilu."""
        }

        form = EditUserForm()
        form.nick.default = user.nick
        form.first_name.default = user.first_name
        form.last_name.default = user.last_name
        form.process()

        return make_response(render_template('user.html', user=user, info=info, form=form), 200)


    @api.response(401, 'Unauthorized — Login required')
    @api.response(303, 'See Other - Correct form')
    @api.expect(api.model('User', User.FIELDS))
    @login_required
    def post(self, user_id):
        user = current_user
        form = EditUserForm()
        info = {
            'title': "Strona twojego profilu",
            'description': """Znajdziesz tutaj wszytkie informacje o swoim profilu."""
        }

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

        return make_response(render_template('user.html', user=user, info=info, form=form), 200)


#================================================================
@api.route('/items')
class ItemsAll(Resource):

    @api.response(200, 'Success - List of items is loaded')
    def get(self):
        items_data = Item.query.all()
        items = list()
        today_date = date.today()
        user = None
        info = {
            'title': "Lista ofert",
            'description': """Znajdziesz tutaj listę wszystkich ofert dostępnych na serwisie.
            Każda oferta zaczyna się dokładnie o 00:00 i kończy o 23:59.
            Zmiana godziny rozpoczęcia jest niemożliwa (przynajmniej na razie)."""
        }

        if current_user.is_authenticated:
            user = {
                'id': current_user.id,
                'nick': current_user.nick,
                'admin': current_user.admin
            }

        for item in items_data:
            if today_date >= item.start_date and today_date <= item.end_date:
                items.append({
                    'id': item.id,
                    'name': item.name,
                    'description': item.description,
                    'start_date': item.start_date,
                    'end_date': item.end_date,
                    'asking_price': item.asking_price,
                    'current_price': item.current_price,
                    'owner': User.query.get(item.owner_id).nick
                })

        return make_response(render_template('item_show_all.html', user=user, info=info, items=items), 200)


@api.route('/item/<int:item_id>')
class ItemOne(Resource):

    @api.response(200, 'Success - Item is loaded')
    def get(self, item_id):
        item_data = Item.query.get(item_id)
        form = NewPriceForm()
        user = None
        info = {
            'title': "Strona oferty",
            'description': """Znajdują się tu wszytkie informacje na temat oferty oraz możliwość podbijania ceny jeśli jest się zalogowanym."""
        }

        if current_user.is_authenticated:
            user = {
                'id': current_user.id,
                'nick': current_user.nick,
                'admin': current_user.admin
            }

        if item_data:
            item = {
                    'id': item_data.id,
                    'name': item_data.name,
                    'description': item_data.description,
                    'start_date': item_data.start_date,
                    'end_date': item_data.end_date,
                    'asking_price': item_data.asking_price,
                    'current_price': item_data.current_price,
                    'owner': User.query.get(item_data.owner_id).nick,
                    'owner_id': item_data.owner_id
                }

            if item_data.winner_id:
                item['winner'] = User.query.get(item_data.winner_id).nick
                item['winner_id'] = item_data.winner_id

            #if not item_data.images:
            #    item['images'] = [{ 'file': "_noimage.jpg", 'alt': "Brak zdjęcia" }]

        return make_response(render_template('item_show_one.html', user=user, info=info, item=item, form=form), 200)


    @api.response(401, 'Unauthorized — Login required')
    @api.response(200, 'Success - Correct change price')
    @login_required
    def post(self, item_id):
        form = NewPriceForm()
        
        if form.validate_on_submit():
            item = Item.query.get(item_id)
            user = {
                'id': current_user.id,
                'nick': current_user.nick,
                'admin': current_user.admin
            }

            if item.current_price < form.new_price.data:
                item.current_price = form.new_price.data
                item.winner_id = user.id

                database.session.add(item)
                database.session.commit()

        return redirect(f'{item_id}', 303)
        


@api.route('/items/add')
class ItemAdd(Resource):

    @api.response(401, 'Unauthorized — Login required')
    @api.response(200, 'Success - Form is loaded')
    @login_required
    def get(self):
        user = current_user
        form = AddItemForm()
        info = {
            'title': "Dodawanie oferty",
            'description': """Widzisz formularz dodawania oferty."""
        }
        
        return make_response(render_template('add_item.html', user=user, info=info, form=form), 200)


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
        info = {
            'title': "Edytuj ofertę",
            'description': """Widzisz formularz oferty który może zawierać informacje zablokowane
            np. nie można zmienić daty rozpoczęcia jeśli ta już się rozpoczeła."""
        }

        form = AddItemForm()
        form.name.default = item.name
        form.description.default = item.description
        form.start_date.default = item.start_date
        form.end_date.default = item.end_date
        form.process()
        
        return make_response(render_template('edit_item.html', user=user, info=info, item=item, today_date=today_date, form=form), 200)


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
