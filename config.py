import os
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config():
    SQLALCHEMY_DATABASE_URI = ('sqlite:///' + os.path.join(BASE_DIR, 'data.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class AdminModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated


    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))
