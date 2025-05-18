from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import IntegerField, FloatField
from wtforms.fields.simple import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, NumberRange
import email_validator

from app.models import User, Category
import sqlalchemy as sa
from app import db



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Jelszó', validators=[DataRequired()])
    submit = SubmitField('Bejelentkezés')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Jelszó', validators=[DataRequired()])
    password_again = PasswordField('Jelszó újra', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Regisztráció')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Ez az email cím már foglalt.')

class AddCategoryForm(FlaskForm):
    name = StringField('Név', validators=[DataRequired(), Length(min=1, max=64)])
    submit = SubmitField('Hozzáadás')

class EditCategoryForm(FlaskForm):
    name = StringField('Név', validators=[DataRequired(), Length(min=1, max=64)])
    submit = SubmitField('Mentés')

# TODO: Min max
class AddSubscriptionForm(FlaskForm):
    name = StringField('Név', validators=[DataRequired(), Length(min=1, max=64)])
    price = FloatField('Ár', validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField('Kategória', coerce=int)
    submit = SubmitField('Hozzáadás')

    def __init__(self, *args, **kwargs):
        super(AddSubscriptionForm, self).__init__(*args, **kwargs)
        categories = db.session.scalars(sa.select(Category).where(current_user.id == Category.user_id)).all()
        self.category.choices = [(category.id, category.name) for category in categories]

class EditSubscriptionForm(FlaskForm):
    name = StringField('Név', validators=[DataRequired(), Length(min=1, max=64)])
    price = FloatField('Ár', validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField('Kategória', coerce=int)
    submit = SubmitField('Mentés')

    def __init__(self, *args, **kwargs):
        super(EditSubscriptionForm, self).__init__(*args, **kwargs)
        categories = db.session.scalars(sa.select(Category).where(current_user.id == Category.user_id)).all()
        self.category.choices = [(category.id, category.name) for category in categories]



