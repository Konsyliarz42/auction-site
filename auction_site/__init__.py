import os
from flask import Flask
from config import Config
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin, AdminIndexView
from flask_bootstrap import Bootstrap

from . import models
from . import routes

from config import Config, AdminModelView

app = Flask(__name__, instance_relative_config=True)
app.config.from_object(Config)
app.config.from_pyfile(os.path.join(app.instance_path, 'config.py'), silent=True)

routes.api.init_app(app)

models.database.init_app(app)
migrate = Migrate(app, models.database)
migrate.init_app(app, models.database)

login_manager = LoginManager()
login_manager.init_app(app)

admin = Admin(app)
admin.add_view(AdminModelView(models.User, models.database.session))
admin.add_view(AdminModelView(models.Item, models.database.session))

Bootstrap(app)

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(user_id)


@app.shell_context_processor
def make_shell_context():
   return {
       "db": models.database,
       "User": models.User,
       "Item": models.Item
   }