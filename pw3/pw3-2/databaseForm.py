from flask import Flask, redirect, request, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form

app = Flask(__name__)
db = SQLAlchemy(app)

class Products(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)
	quantity = db.Column(db.Integer, nullable=False)

ProductForm = model_form(Products, base_class=FlaskForm, db_session=db.session)

@app.before_first_request
def initMe():
	db.create_all()

	product1 = Products(name="Banana", quantity=5)
	product2 = Products(name="Tuna Fish", quantity=100)
	product3 = Products(name="Milk Carton", quantity=40)

	db.session.add_all([product1, product2, product3])
	db.session.commit()

@app.route("/")
def index():
	print(Products.query.first().name)
	return render_template("index.html", products=Products.query.all())

if __name__ == "__main__":
	app.run()
