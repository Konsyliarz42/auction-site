from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField
from wtforms.validators import InputRequired, Length

class LoginForm(FlaskForm):
    nick = StringField('Nick', validators=[InputRequired()])
    password = PasswordField('Hasło', validators=[InputRequired()])


class RegisterForm(FlaskForm):
    nick = StringField('Nick', validators=[InputRequired(), Length(max=256)])
    password = PasswordField('Hasło', validators=[InputRequired(), Length(max=256)])
    first_name = StringField('Imię', validators=[Length(max=256)])
    last_name = StringField('Nazwisko', validators=[Length(max=256)])


class NewPriceForm(FlaskForm):
    new_price = FloatField('Nowa cena')


class EditUser(FlaskForm):
    nick = StringField('Nick', validators=[Length(max=256)])
    first_name = StringField('Imię', validators=[Length(max=256)])
    last_name = StringField('Nazwisko', validators=[Length(max=256)])
