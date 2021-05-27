from flask import Flask, render_template, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form

app = Flask(__name__)
app.secret_key = "ajah8da<th9oov4AerootuquaiVoo8"
db = SQLAlchemy(app)

class MovieQuote(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)
	quote = db.Column(db.String, nullable=False)

MovieQuoteForm = model_form(MovieQuote, base_class=FlaskForm, db_session=db.session)

@app.before_first_request
def initDB():
	db.create_all()

	movieQuote = MovieQuote(name="Blade Runner", quote="I saw C-beams glitter in the dark.")
	db.session.add(movieQuote)

	movieQuote = MovieQuote(name="Blade Runner", quote="A light that burns twice as bright burns half as long.")
	db.session.add(movieQuote)

	movieQuote = MovieQuote(name="Prisoner", quote="I will not be pushed, files, stamped, indexed, briefed, debriefed, or numbered!")
	db.session.add(movieQuote)

	db.session.commit()

@app.route("/<int:id>/delete")
def deleteMovieQuote(id):
	movieQuote = MovieQuote.query.get_or_404(id)
	db.session.delete(movieQuote)
	db.session.commit()

	flash("Entry deleted")
	return redirect("/")

@app.route("/<int:id>/edit", methods=["GET","POST"])

@app.route("/new", methods=["GET", "POST"])
def newMovieQuote(id=None):
	movieQuote = MovieQuote()
	if id:
		movieQuote = MovieQuote.query.get_or_404(id)
	form = MovieQuoteForm(obj=movieQuote)

	if form.validate_on_submit():
		form.populate_obj(movieQuote)

		db.session.add(movieQuote)
		db.session.commit()

		flash("Added a new movie/TV quote")
		return redirect("/")

	return render_template("new2.html", form=form)

@app.route("/")
def index():
	movieQuotes = MovieQuote.query.all()
	return render_template("index2.html", movieQuotes=movieQuotes)

if __name__ == "__main__":
	app.run()
