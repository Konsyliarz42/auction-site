from flask import Flask
from config import Config
from flask_migrate import Migrate

from . import models
from . import routes

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

routes.api.init_app(app)
models.database.init_app(app)
migrate = Migrate(app, models.database)
migrate.init_app(app, models.database)