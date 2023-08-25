from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cashflow.db'
db = SQLAlchemy(app)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    limit = db.Column(db.Float, nullable=False)
    expenses = db.relationship('Expense', backref='budget', lazy=True)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id'), nullable=False)

@app.route('/create_budget', methods=['POST'])
def create_budget():
    data = request.get_json()
    category = data['category']
    limit = data['limit']
    new_budget = Budget(category=category, limit=limit)
    db.session.add(new_budget)
    try:
        db.session.commit()
        return jsonify({"message": "Budget created successfully"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Category already exists"}), 400

@app.route('/add_expense', methods=['POST'])
def add_expense():
    data = request.get_json()
    category = data['category']
    amount = data['amount']
    budget = Budget.query.filter_by(category=category).first()
    if not budget:
        return jsonify({"message": "Budget not found"}), 404
    new_expense = Expense(category=category, amount=amount, budget=budget)
    db.session.add(new_expense)
    db.session.commit()
    return jsonify({"message": "Expense added successfully"}), 201

@app.route('/get_budget_status', methods=['GET'])
def get_budget_status():
    budget_status = []
    budgets = Budget.query.all()
    for budget in budgets:
        total_expenses = sum(expense.amount for expense in budget.expenses)
        budget_status.append({"category": budget.category, "spent": total_expenses, "limit": budget.limit})
    return jsonify({"budget_status": budget_status})

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
