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

from flask import Flask, render_template, flash, redirect, session, abort, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms.ext.sqlalchemy.orm import model_form
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, SelectField, PasswordField, validators, HiddenField
from datetime import date

app = Flask(__name__)
csrf = CSRFProtect(app)
#app.secret_key = 
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql:///juuso'
db = SQLAlchemy(app)

class Groups(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)
	gameType = db.Column(db.String, nullable=False)
	passwordHash = db.Column(db.String, nullable=True)
	friend_id = db.relationship("User", backref=db.backref("groups"), lazy=True)
	score_id = db.relationship("Scorekeep", backref=db.backref("groups"), lazy=True)
#	history_id = db.relationship("History", backref=db.backref("groups"), lazy=True)

	def setGroupPassword(self, password):
		self.passwordHash = generate_password_hash(password)

	def checkGroupPassword(self, password):
		return check_password_hash(self.passwordHash, password)

class GroupsForm(FlaskForm):
	name = StringField("Group Name", validators=[validators.InputRequired()])
	password = PasswordField("Password", validators=[validators.InputRequired()])
	gameType = SelectField("Game Type", choices=[('301', '301'), ('501', '501')])
class GroupsJoinForm(FlaskForm):
	name = HiddenField()
	password = PasswordField("password", validators=[validators.InputRequired()])


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String, unique=True, nullable=False)
	passwordHash = db.Column(db.String, nullable=False)
	scorekeep_id = db.relationship("Scorekeep", backref=db.backref("user"), lazy=True)
	groupId = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=True)

	def setPassword(self, password):
		self.passwordHash = generate_password_hash(password)

	def checkPassword(self, password):
		return check_password_hash(self.passwordHash, password)

class UserForm(FlaskForm):
	email = StringField("email", validators=[validators.Email()])
	password = PasswordField("password", validators=[validators.InputRequired()])


class Scorekeep(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, unique=True, nullable=False)
	score = db.Column(db.Integer, nullable=False)
	addedScore = db.Column(db.Integer, nullable=True)

	userId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
	groupId = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=True)

ScorekeepForm = model_form(Scorekeep, base_class=FlaskForm, db_session=db.session, exclude=("score","addedScore","user","groups"))
ScorekeepEditForm = model_form(Scorekeep, base_class=FlaskForm, db_session=db.session, exclude=("score","name","user","groups"))

#class History(db.Model):
#	id = db.Column(db.Integer, primary_key=True)
#	gameHistory = db.Column(db.String, nullable=False)
#	dateOfGame = db.Column(db.String, nullable=False)
#	groupId = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=True)

#class HistoryForm(FlaskForm):
#	gameHistory = HiddenField()
#	dateOfGame = HiddenField()

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

def groupRequired():
	if not currentGroup():
		abort(403)

def currentGroup():
	try:
		gid = int(session["gid"])
	except:
		return None
	if gid == 1:
		return None
	return Groups.query.get(gid)

app.jinja_env.globals["currentGroup"] = currentGroup

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
		session["gid"]=1
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

		user.groupId = 1

		db.session.add(user)
		db.session.commit()

		flash("Registration successful. Welcome to throw darts!")
		return redirect("/")
	return render_template("register.html", form=form, viewKey=1)

@app.route("/user/logout")
def logoutView():
	session["uid"] = None
	session["gid"] = 1
	flash("Logged out.")
	return redirect("/")


@app.route("/user/groups/create", methods=["GET", "POST"])
def createGroupView():
	loginRequired()

	form = GroupsForm()
	if form.validate_on_submit():
		name = form.name.data
		gameType = form.gameType.data
		password = form.password.data

		if Groups.query.filter_by(name=name).first():
			flash("Group already exists!")
			return redirect("/user/groups/create")

		groups = Groups(name=name, gameType=gameType)
		groups.setGroupPassword(password)

		db.session.add(groups)
		db.session.commit()

		user = User.query.get(session["uid"])
		user.groupId = groups.id
		db.session.commit()

		flash("New Darts group created. Share the password only with your group members!")
		return redirect("/")
	return render_template("register.html", form=form, viewKey=2)

@app.route("/groups", methods=["GET", "POST"])
def listGroups():
	loginRequired()
	if currentGroup != None:
		gid = session["gid"]
		flash(gid)
	else:
		gid = 1
	groups = Groups.query.all()
	return render_template("groupList.html", groups=groups, gid=gid)

@app.route("/groups/<int:id>/login", methods=["GET", "POST"])
def joinGroupView(id=None):
	loginRequired()

	name = request.form.get("name")
	form = GroupsJoinForm(name = name)

	if form.validate_on_submit():
		password = form.password.data
		groups = Groups.query.filter_by(name=name).first()
		if not groups:
			flash("Failed to join group. Reason: Group does not exist.")
			print("No such group")
			return redirect("/groups")
		if not groups.checkGroupPassword(password):
			flash("Failed to join the group. Reason: Wrong password.")
			print("Wrong password")
			return redirect("/groups")

		user = User.query.get(session["uid"])
		user.groupId = groups.id
		db.session.commit()

		session["gid"]=groups.id
		flash("Successfully joined session.")

		return redirect("/")

	return render_template("login.html", form=form)


@app.route("/groups/logout")
def groupLogoutView():
	session["gid"] = 1
	user = User.query.get(session["uid"])
	user.groupId = 1
	db.session.commit()

	flash("Game Session left.")
	return redirect("/")

## The main view

@app.before_first_request
def initDB():
	db.create_all()

	#BECUSE HISTORY CLASS DID NOT WORK OUT, THIS REMAINS USELESS
	# create a default history entry, use it for logging
#	histories = History.query.all()
#	if len(histories) == 0:
#		histories = History(gameHistory="Filler",dateOfGame=date.today())
#		db.session.add(histories)

	# check if database has any groups, if not or if "Lobby" does
	# not exist, then create it as the default open group for all logins
	groups = Groups.query.all()
	if len(groups) == 0:
		session["gid"] = 1
		lobby = Groups(name="Lobby", gameType=0)
		db.session.add(lobby)
	else:
		# this might be a wrong way to create the default group
		# I should change this in case of future problems
		if groups[0].name != "Lobby":
			lobby = Groups(name="Lobby", gameType=0)
			db.session.add(lobby)

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
		if scorekeep.addedScore == None:
			flash("No input.")
			return redirect(request.url)
		elif scorekeep.addedScore < 0:
			flash("Your round score cannot be negative!")
			return redirect(request.url)
		elif scorekeep.addedScore > 180:
			flash("Maximum possible round score is 180 points!")
			return redirect(request.url)
		scorekeep.score = scorekeep.score - scorekeep.addedScore
		if scorekeep.score < 0:
			scorekeep.score = 0

		db.session.add(scorekeep)
		db.session.commit()
		return redirect("/")
	return render_template("new.html", form=form)

@app.route("/groups/<int:id>/nullify")
def nullifyScores(id):
	loginRequired()
	groupRequired()
	if id:
		group = Groups.query.get_or_404(id)
		scorekeep = Scorekeep.query.all()
		for scorekeep in scorekeep:
			if scorekeep.groupId == group.id:
				if group.gameType == "501":
					scorekeep.score = 501
					db.session.commit()
				elif group.gameType == "301":
					scorekeep.score = 301
					db.session.commit()
	return redirect("/")

@app.route("/<int:id>/delete")
def deleteScore(id):
	loginRequired()
	groupRequired()
	if id:
		scorekeep = Scorekeep.query.get_or_404(id)
		db.session.delete(scorekeep)
		db.session.commit()
		return redirect("/")
	else:
		abort(403)

@app.route("/new", methods=["GET", "POST"])
def newScore(id=None):
	loginRequired()
	groupRequired()

	group = Groups.query.get(session["gid"])
	if group.id != 1:
		initScore = int(group.gameType)

	scorekeep = Scorekeep()
	if id:
		scorekeep = Scorekeep.query.get_or_404(id)

	form = ScorekeepForm(obj=scorekeep)
	if form.validate_on_submit():
		form.populate_obj(scorekeep)

		scorekeep.score = initScore

		## set id-relationship between classes
		scorekeep.user = User.query.get(session["uid"])
		scorekeep.groups = Groups.query.get(session["gid"])

		db.session.add(scorekeep)
		db.session.commit()

		flash("Score situation updated!")
		return redirect("/")
	return render_template("new.html", form=form)

@app.route("/")
def index():
	groups = Groups.query.all()

	scorekeep = Scorekeep.query.all()
	scorekeep.sort(key=lambda x: x.score)
	if currentUser():
		#userId = currentUser().id
		user = User.query.get(session["uid"])
		return render_template("index.html", scorekeep=scorekeep, user=user, groups=groups)
	return render_template("index.html", scorekeep=scorekeep, groups=groups)
