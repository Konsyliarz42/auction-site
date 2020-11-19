from flask import Flask
from config import Config
from flask_migrate import Migrate
from flask_login import LoginManager

from . import models
from . import routes

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

app.config['SECRET_KEY'] = 'testSecretKeyForAWhile'

routes.api.init_app(app)
models.database.init_app(app)
migrate = Migrate(app, models.database)
migrate.init_app(app, models.database)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))