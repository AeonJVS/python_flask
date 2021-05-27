from flask import Flask, render_template, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form

app = Flask(__name__)
app.secret_key = "wue8eingee?keiphei2Ri&e0aeng4i"
db = SQLAlchemy(app)

class Address(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	namefirst = db.Column(db.String, nullable=False)
	namelast = db.Column(db.String, nullable=False)
	email = db.Column(db.String, unique=True, nullable=False)
	pnumber = db.Column(db.Integer, nullable=False)
	favcol = db.Column(db.String, nullable=False)

AddressForm = model_form(Address, base_class=FlaskForm, db_session=db.session)

@app.before_first_request
def initDB():
	db.create_all()

	address = Address(namefirst="Frank", namelast="Irish", email="firish@fakemail.com", pnumber="5553450393", favcol="Green")
	db.session.add(address)
	address = Address(namefirst="Sarah", namelast="Browning", email="s.brown@fakemail.com", pnumber="55534574573", favcol="Red")
	db.session.add(address)
	address = Address(namefirst="John", namelast="Johnson", email="j.j@fakemail.com", pnumber="5553486543", favcol="Purple")
	db.session.add(address)
	address = Address(namefirst="Laura", namelast="Branigan", email="selfcontrol@fakemail.com", pnumber="5553469348", favcol="Crimson")
	db.session.add(address)

	db.session.commit()

@app.route("/<int:id>/edit", methods=["GET", "POST"])
@app.route("/add+new", methods=["GET", "POST"])
def newAddress(id=None):
	address = Address()
	if id:
		address = Address.query.get(id)

	form = AddressForm(obj=address)

	if form.validate_on_submit():
		form.populate_obj(address)
		db.session.add(address)
		db.session.commit()

		flash("New address added.")
		return redirect("/")

	return render_template("new.html", form=form)

@app.route("/<int:id>/delete")
def deleteAddress(id):
	address = Address.query.get_or_404(id)
	db.session.delete(address)
	db.session.commit()

	flash("Address deleted.")
	return redirect("/")

@app.route("/")
def index():
	addresses = Address.query.all()
	return render_template("index.html", addresses=addresses)

if __name__ == "__main__":
	app.run()
