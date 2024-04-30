from __future__ import print_function
from app.Controller.auth_forms import RegistrationForm, LoginForm, AdminRegForm
from flask_login import login_user, logout_user, current_user, login_required
import sys
from flask import Blueprint
from flask import render_template, flash, redirect, url_for
#from flask_sqlalchemy import sqlalchemy
from config import Config
from app.Model.models import User
from app import db

bp_auth = Blueprint('auth', __name__)
bp_auth.template_folder = Config.TEMPLATE_FOLDER 

'''
@bp_auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.admin == 1 :
            return redirect(url_for('routes.admin_index'))
        return redirect(url_for('routes.index'))
    rform=RegistrationForm()
    if rform.validate_on_submit():
        user= User(username=rform.username.data, email=rform.email.data, firstname = rform.firstname.data, lastname = rform.lastname.data, admin = 0)
        user.set_password(rform.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('routes.index'))
    return render_template('register.html', form=rform)
'''
@bp_auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.admin == 1 :
            return redirect(url_for('routes.admin_index'))
        return redirect(url_for('routes.index'))

    rform = RegistrationForm()
    if rform.validate_on_submit():
        user = User(
            username=rform.username.data,
            email=rform.email.data,
            firstname=rform.firstname.data,
            lastname=rform.lastname.data,
            admin=0
        )
        user.set_password(rform.password.data)
        # Insert new user document into mongo collection
        user.save()  # Save the user to MongoDB
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('routes.index'))
    return render_template('register.html', form=rform)


@bp_auth.route('/registerAdmin', methods=['GET', 'POST'])
def registerAdmin():
    if current_user.is_authenticated:
        if current_user.admin == 1:
            return redirect(url_for('routes.admin_index'))
        return redirect(url_for('routes.index'))

    rform = AdminRegForm()

    if rform.validate_on_submit():
        if rform.adminCode.data != "1234":
            flash("Incorrect admin code")
            return redirect(url_for('auth.registerAdmin'))

        user = User(username=rform.username.data, email=rform.email.data, firstname=rform.firstname.data, lastname=rform.lastname.data, admin=1)
        user.set_password(rform.password.data)
        user.save()

        flash('Congratulations, you are now a registered admin!')
        return redirect(url_for('routes.admin_index'))

    return render_template('admin_reg.html', form=rform)

'''
@bp_auth.route('/registerAdmin', methods=['GET', 'POST'])
def registerAdmin():
    if current_user.is_authenticated:
        if current_user.admin == 1 :
            return redirect(url_for('routes.admin_index'))
        return redirect(url_for('routes.index'))
    rform=AdminRegForm()
    if rform.validate_on_submit():
        if(rform.adminCode.data!="1234"):
            print(rform.adminCode)
            flash("Incorrect admin code")
            return redirect(url_for('auth.registerAdmin'))
        user= User(username=rform.username.data, email=rform.email.data, firstname = rform.firstname.data, lastname = rform.lastname.data, admin = 1)
        user.set_password(rform.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered admin!')
        return redirect(url_for('routes.admin_index'))
    return render_template('admin_reg.html', form=rform)
'''
'''
@bp_auth.route('/login',methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.admin == 1 :
            return redirect(url_for('routes.admin_index'))
        return redirect(url_for('routes.index'))
    lform=LoginForm()
    if lform.validate_on_submit():
        user=User.query.filter_by(username=lform.username.data).first()
        if (user is not None) and (user.get_password(lform.password.data)==True):
            login_user(user,remember=lform.remember_me.data)
            if(user.admin==1):
                return redirect(url_for('routes.admin_index'))
            return redirect(url_for('routes.index'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
    return render_template('login.html',title='Sign in',form=lform)
'''
@bp_auth.route('/login',methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.admin == 1:
            return redirect(url_for('routes.admin_index'))
        return redirect(url_for('routes.index'))

    lform = LoginForm()

    if lform.validate_on_submit():
        user = User.objects(username=lform.username.data).first()

        if user and user.get_password(lform.password.data):
            login_user(user, remember=lform.remember_me.data)

            if user.admin == 1:
                return redirect(url_for('routes.admin_index'))
            return redirect(url_for('routes.index'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))

    return render_template('login.html', title='Sign in', form=lform)


@bp_auth.route('/logout',methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))