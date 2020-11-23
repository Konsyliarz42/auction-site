from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, TextAreaField, DateField
from wtforms.validators import InputRequired, Length
from datetime import date

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


class EditUserForm(FlaskForm):
    nick = StringField('Nick', validators=[Length(max=256)])
    first_name = StringField('Imię', validators=[Length(max=256)])
    last_name = StringField('Nazwisko', validators=[Length(max=256)])


class AddItemForm(FlaskForm):
    name = StringField("Nazwa", validators=[InputRequired(), Length(max=256)])
    description = TextAreaField("Opis", validators=[Length(max=2048)])
    asking_price = FloatField("Cena wywoławcza", validators=[InputRequired()], default=0.0)
    start_date = DateField("Data rozpoczęcia", validators=[InputRequired()], default=date.today())
    end_date = DateField("Data zakończenia", validators=[InputRequired()], default=date.today())


class EditItemForm(FlaskForm):
    name = StringField("Nazwa", validators=[Length(max=256)])
    description = TextAreaField("Opis", validators=[Length(max=2048)])
    asking_price = FloatField("Cena wywoławcza", default=0.0)
    start_date = DateField("Data rozpoczęcia", default=date.today())
    end_date = DateField("Data zakończenia", default=date.today())