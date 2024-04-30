from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Length, Email
from app.Model.models import User
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Register')

    '''
    def validate_username(self,username):
        user= User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('The username already exists! Please use a different username.')
'''
    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user:
            raise ValidationError('The username already exists! Please use a different username.')

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user:
            raise ValidationError('The email already exists! Please use a different email address.')
'''
    def validate_email(self,email):
        user= User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('The email already exists! Please use a different email address.')
'''

class AdminRegForm(FlaskForm):
    adminCode=StringField("Admin Code",validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    password2 = PasswordField('Repeat Password',validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user:
            raise ValidationError('The username already exists! Please use a different username.')

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user:
            raise ValidationError('The email already exists! Please use a different email address.')

'''
    def validate_username(self,username):
        user= User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('The username already exists! Please use a different username.')


    def validate_email(self,email):
        user= User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('The email already exists! Please use a different email address.')
'''
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember_me=BooleanField('Remember me')
    submit = SubmitField('Sign In')