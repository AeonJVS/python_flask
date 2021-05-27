from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form

app = Flask(__name__)
app.secret_key = "AiTh8Ui/xo2aeng2uG8Aih8eepahTh"
db = SQLAlchemy(app)

class CoffeeBrand(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)

CoffeeBrandForm = model_form(CoffeeBrand, base_class=FlaskForm, db_session=db.session)

@app.before_first_request
def initDB():
	db.create_all()
	coffeeBrand = CoffeeBrand(name="Löfberg")
	db.session.add(coffeeBrand)

	coffeeBrand = CoffeeBrand(name="Juhla Mokka")
	db.session.add(coffeeBrand)

	db.session.commit()

@app.route("/add+new", methods=["GET", "POST"])
def newCoffeeBrand():
	form = CoffeeBrandForm()

	if form.validate_on_submit():
		coffeeBrand = CoffeeBrand()
		form.populate_obj(coffeeBrand)

		db.session.add(coffeeBrand)
		db.session.commit()

		print("Coffee brand added successfully")

	return render_template("addNew.html", form=form)

@app.route("/")
def index():
	coffeeBrands = CoffeeBrand.query.all()
	return render_template("index.html", coffeeBrands=coffeeBrands)

if __name__ == "__main__":
	app.run()
