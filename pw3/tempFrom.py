from flask import Flask, flash, redirect, request, url_for, render_template
from flask_sqlalchemy import SQLAlchemy #sudo apt-get install python3-flask-sqlalchemy

from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form

app = Flask(__name__)
app.secret_key = "ieY1thoth5eed*eepugi8AeSei>j6r"
db = SQLAlchemy(app)

class Greatmen(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)

GreatmanForm = model_form(Greatmen, base_class=FlaskForm, db_session=db.session)

@app.before_first_request
def initMe():
	db.create_all()

	greatman1 = Greatmen(name="Caracalla")
	greatman2 = Greatmen(name="Nero")
	greatman3 = Greatmen(name="Caligula")

	db.session.add_all([greatman1, greatman2, greatman3])
	db.session.commit()

@app.route("/msg")
def msgPage():
	flash("Here's a message!")
	return redirect("/")

@app.route("/new", methods=["GET", "POST"])
def addForm():
	form = GreatmanForm()
	#print(request.form)
	return render_template("new.html", form=form)

@app.route("/")

def index():
	print(Greatmen.query.first().name)
	return render_template("index.html", greatmen=Greatmen.query.all())

if __name__ == "__main__":
	app.run()
