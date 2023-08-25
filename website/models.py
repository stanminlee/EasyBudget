# file contains the database models used for storing user login information and budgetting data

from . import db 
from flask_login import UserMixin
from sqlalchemy.sql import func

# for income
class Income(db.Model):
    id = db.Column(db.Integer, primary_key = True)

    # data for the income
    total = db.Column(db.Float, nullable = False)

    date = db.Column(db.DateTime(timezone = True), default = func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# for expenses
class Expense(db.Model):
    # establishing the primary keys
    id = db.Column(db.Integer, primary_key = True)

    # data for the expenses
    amount = db.Column(db.Float, nullable = False)
    name = db.Column(db.String(255), nullable = False)


    date = db.Column(db.DateTime(timezone = True), default = func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# for users
class User(db.Model, UserMixin):
    # establishing the primary keys
    id = db.Column(db.Integer, primary_key = True)

    # establishing the login information
    email = db.Column(db.String(100), unique = True) 
    password = db.Column(db.String(100))
    first_name = db.Column(db.String(100))

    total_income = db.Column(db.Float, default = 0.0)

    expenses = db.relationship('Expense')
    income = db.relationship('Income', uselist = False)