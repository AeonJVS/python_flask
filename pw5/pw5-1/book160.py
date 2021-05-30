from flask import Flask, render_template, flash, redirect, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form

from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, validators

app = Flask(__name__)
app.secret_key = "aiCa5soo5ieg5iu2Hae2gaaxeephie"
db = SQLAlchemy(app)

class Entry(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	author = db.Column(db.String, nullable=False)
	bookname = db.Column(db.String, nullable=False)
	summary = db.Column(db.String(160), nullable=False)

EntryForm = model_form(Entry, base_class=FlaskForm, db_session=db.session)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String, nullable=False, unique=True)
	passwordHash = db.Column(db.String, nullable=False)

	def setPassword(self, password):
		self.passwordHash = generate_password_hash(password)

	def checkPassword(self, password):
		return check_password_hash(self.passwordHash, password)

class UserForm(FlaskForm):
	email = StringField("email", validators=[validators.Email()])
	password = PasswordField("password", validators=[validators.InputRequired()])

## User utility

def loginRequired():
	if not currentUser():
		abort(403)

def currentUser():
	try:
		uid = int(session["uid"])
	except:
		return None
	return User.query.get(uid)

app.jinja_env.globals["currentUser"] = currentUser

## User view

@app.route("/user/login", methods=["GET", "POST"])
def loginView():
	form = UserForm()

	if form.validate_on_submit():
		email = form.email.data
		password = form.password.data

		user = User.query.filter_by(email=email).first()
		if not user:
			flash("Login failed.")
			print("No such user")
			return redirect("/user/login")
		if not user.checkPassword(password):
			flash("Login failed.")
			print("Wrong password")
			return redirect("/user/login")

		session["uid"]=user.id
		flash("Login successful.")
		return redirect("/")

	return render_template("login.html", form=form)

@app.route("/user/register", methods=["GET", "POST"])
def registerView():
	form = UserForm()
	if form.validate_on_submit():
		email = form.email.data

		password = form.password.data

		if User.query.filter_by(email=email).first():
			flash("User already exists! Please log in.")
			return redirect("/user/login")

		user = User(email=email)
		user.setPassword(password)

		db.session.add(user)
		db.session.commit()

		flash("Registration successful. Welcome!")
		return redirect("/user/login")
	return render_template("register.html", form=form)

@app.route("/user/logout")
def logoutView():
	session["uid"] = None
	flash("Logged out.")
	return redirect("/")

## The main view

@app.before_first_request
def initDB():
	db.create_all()

	entry = Entry(author="J.R.R. Tolkien", bookname="The Lord of The Rings", summary="In the land of Middle-Earth, a little hobbit is forced by fate to carry a ring containing the lifeforce of a dark lord and destroy it before it is too late.")
	db.session.add(entry)

	db.session.commit()

@app.errorhandler(404)
def custom404(e):
	return render_template("404.html")

@app.route("/new", methods=["GET", "POST"])
def newEntry(id=None):
	loginRequired()

	entry = Entry()
	if id:
		entry = Entry.query.get_or_404(id)
	form = EntryForm(obj=entry)

	if form.validate_on_submit():
		form.populate_obj(entry)

#		if len(entry.summary) > 160:
#			flash("You summary is too long.")
#			return redirect("/new")

		db.session.add(entry)
		db.session.commit()

		flash("Entry added")
		return redirect("/")
	return render_template("new.html", form=form)

@app.route("/")
def index():
	entry = Entry.query.all()
	return render_template("index.html", entry=entry)

if __name__ == "__main__":
	app.run()
