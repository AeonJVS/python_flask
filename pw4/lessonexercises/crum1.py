from flask import Flask, render_template, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form

app = Flask(__name__)
app.secret_key = "phi3gic1hee:Ng3poo.ch^eijei2ju"
db = SQLAlchemy(app)

class RetroCar(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)
	manufacturer = db.Column(db.String, nullable=False)
	color = db.Column(db.String, nullable=False)

RetroCarForm = model_form(RetroCar, base_class=FlaskForm, db_session=db.session)

@app.before_first_request
def initDB():
	db.create_all()

	retroCar = RetroCar(name="Testarossa", manufacturer="Ferrari", color="White")
	db.session.add(retroCar)
	retroCar = RetroCar(name="Countach", manufacturer="Lamborghini", color="White")
	db.session.add(retroCar)

	db.session.commit()

@app.route("/new", methods=["GET", "POST"])
def newCar():
	form = RetroCarForm()

	if form.validate_on_submit():
		retroCar = RetroCar()
		form.populate_obj(retroCar)

		db.session.add(retroCar)
		db.session.commit()

		flash("Added a new retro car in the database.")
		redirect("/")

	return render_template("new.html", form=form)

@app.route("/")
def index():
	retroCars = RetroCar.query.all()
	return render_template("index1.html", retroCars=retroCars)

if __name__ == "__main__":
	app.run()
