# file contains the interface for the expense tracking

from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Expense, Income
from . import db
import json
from sqlalchemy import func

views = Blueprint('views', __name__)

# all requests are handled here and passed to other functions
@views.route('/', methods = ['GET', 'POST'])
@login_required
def home():
    user = current_user
    if request.method == 'POST':

        action = request.form.get('action')
        
        if action == 'expense':
            handle_expense(user)
        elif action == 'income':
            handle_income(user)

    total_income = user.income.total if user.income else 0.0
    total_expenses = db.session.query(func.sum(Expense.amount)).filter(Expense.user_id == user.id).scalar() or 0.0
    savings = float(total_income) * 0.2

    # checks whether the total expenses value is too high (based on the 50/30/20 rule)
    # makes suggestions to the user to reevaluate their budget
    if (float(total_expenses) >= float(total_income) * 0.8 and float(total_income) != 0.0):
        
        remaining_balance = float(total_income) - float(total_expenses)
        
        if remaining_balance > 0:
            flash('Your expenses are exceeding 80 percent of your total income.\
              You should aim to save 20 percent of your income for emergency use or investments'
              , category = 'error')
            savings = float(total_income) - float(total_expenses)
            remaining_balance = 0
        elif remaining_balance < 0:
            flash('Due to your negative remaining balance, you will need to use your current savings to make it \
              through the month'
              , category = 'error')
            savings = 0
    else:
        remaining_balance = float(total_income) - float(savings) - float(total_expenses)

    return render_template("home.html", user = user, 
                           total_expenses = total_expenses, 
                           total_income = total_income, 
                           savings = savings, 
                           remaining_balance = remaining_balance)


"""
The two functions handle_expense and handle_income are used to check for invalid inputs (negative number, empty entry, etc.)
and add valid inputs into the database.
"""

# handling an expense input
def handle_expense(user):
        expense_name = request.form.get('expense_name')
        expense_amount = request.form.get('expense_amount')

        try:
            expense_amount = float(expense_amount)
            if len(expense_name) < 1 or expense_amount <= 0:
                flash('Invalid expense data', category = 'error')
            else:
                new_expense = Expense(name = expense_name, amount = expense_amount, user_id = user.id)
                db.session.add(new_expense)
                db.session.commit()
        except ValueError:
            flash('Please enter a valid amount for the expense', category = 'error')

# handling an income input
def handle_income(user):
    income_value = request.form.get('income')

    try:
        income_value = float(income_value)
        if income_value < 0:
            flash('Invalid income value', category='error')
        else:
            if user.income:
                user.income.total = income_value
                db.session.commit()
            else:
                new_income = Income(total=income_value, user_id=user.id)
                db.session.add(new_income)
                db.session.commit()
    except ValueError:
        flash('Please enter a numeric value for income', category='error')


# handling a deletion of an expense
@views.route('/delete-expense', methods=['POST'])
def delete_expense():
    expense_data = json.loads(request.data)
    expense_id = expense_data['expenseId']
    expense = Expense.query.get(expense_id)

    if expense and expense.user_id == current_user.id:
        db.session.delete(expense)
        db.session.commit()

    return jsonify({})