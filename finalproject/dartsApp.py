#DartsApp is a simple score-keeping application for the game of Darts.
#
#Demo is usable at 139.162.154.116 for at least the duration of the course
#"Python Web Service From Idea to Production" held by Tero Karvinen.
#
#Please keep in mind, that this application is in Alpha phase of its
#software release life cycle and will probably remain as such. This means
#that parts of the application may fail due to errors, crash or
#experience data loss.

#Copyright (C) 2021 Juuso Ihatsu
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from flask import Flask, render_template, flash, redirect, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms.ext.sqlalchemy.orm import model_form
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, validators

app = Flask(__name__)
#app.secret_key    --- removed for security purposes
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql:///juuso'
db = SQLAlchemy(app)

class Scorekeep(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, unique=True, nullable=False)
	score = db.Column(db.Integer, nullable=False)
	addedScore = db.Column(db.Integer, nullable=True)

ScorekeepForm = model_form(Scorekeep, base_class=FlaskForm, db_session=db.session, exclude=("score","addedScore"))
ScorekeepEditForm = model_form(Scorekeep, base_class=FlaskForm, db_session=db.session, exclude=("score","name"))

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String, unique=True, nullable=False)
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

		flash("Registration successful. Welcome to throw darts!")
		return redirect("/")
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

	db.session.commit()

@app.errorhandler(404)
def custom404(e):
	return render_template("404.html")

@app.route("/<int:id>/edit", methods=["GET", "POST"])
def editScore(id=None):
	loginRequired()

	scorekeep = Scorekeep()
	if id:
		scorekeep = Scorekeep.query.get_or_404(id)
	form = ScorekeepEditForm(obj=scorekeep)
	if form.validate_on_submit():
		form.populate_obj(scorekeep)
		scorekeep.score = scorekeep.score - scorekeep.addedScore

		db.session.add(scorekeep)
		db.session.commit()
		return redirect("/")
	return render_template("new.html", form=form)

@app.route("/new", methods=["GET", "POST"])
def newScore(id=None):
	loginRequired()

	scorekeep = Scorekeep()
	if id:
		scorekeep = Scorekeep.query.get_or_404(id)

	form = ScorekeepForm(obj=scorekeep)
	if form.validate_on_submit():
		form.populate_obj(scorekeep)

		scorekeep.score = 501

		scorekeep.user = User.query.get(session["uid"])

		db.session.add(scorekeep)
		db.session.commit()

		flash("Score situation updated!")
		return redirect("/")
	return render_template("new.html", form=form)

@app.route("/")
def index():
	scorekeep = Scorekeep.query.all()
	return render_template("index.html", scorekeep=scorekeep)

