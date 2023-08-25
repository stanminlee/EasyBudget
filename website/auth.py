# this file is used for authenticating users
# account validation, creation, and storage is handled here

from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, logout_user, current_user
import re

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # look for the specific user and check whether there is a registered account for the entered email address
        user = User.query.filter_by(email = email).first()
        if user:
            # check if the entered password matches the one stored for the account
            # if so, redirect to the homepage otherwise tell them to enter the correct password
            if check_password_hash(user.password, password):
                flash('Logged in successfully', category = 'success')
                login_user(user, remember = True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect Password', category = 'error')
        else:
            flash('The email you have entered does not have a registered account', category = 'error')

    return render_template("login.html", user = current_user)



# logging users out
@auth.route('/logout')
def logout():
    logout_user()
    return render_template("login.html", user = current_user)



# signing users in
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        
        # gather necessary information from the inputted details
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        user = User.query.filter_by(email = email).first()

        # the new user must not have a registered account, and they must have a password following the specified parameters
        # valid email address, valid first name, password length > 6, capital letter in the password
        if user:
            flash("The email you have entered already has a registered account", category= "error")
        # use a regular expression to validate an email address
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Must enter a valid email address", category = "error")
        elif len(first_name) < 1:
            flash("Must enter a valid first name", category = "error")
        elif len(password1) < 7:
            flash("Password must be longer than 6 characters", category = "error")
        elif not any(ch.isupper() for ch in password1):
            flash("Password must contain a capital letter", category = "error")
        elif password1 != password2:
            flash("Passwords do not match", category = "error")
        else:
            # create user with the email, first name, and hashed password using sha256 hashing method
            # add all of the data to the database and redirect to the homepage
            new_user = User(email = email, first_name = first_name, password = generate_password_hash(password1, method = 'sha256'))
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user, remember = True)
            flash("Account was created successfully.", category = "success")
            return redirect(url_for('views.home'))

    return render_template("signup.html", user = current_user)