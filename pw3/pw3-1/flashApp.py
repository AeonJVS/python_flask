from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "quohbu8Tohwee8tu)e1quie?y5ihee8ceiquahyohooz=a1aNga7pheCh2ch"

@app.route("/secret")
def secret():
	secret = "Near a tree by a river there's a hole in the ground where an old man of Aran goes around and around..."
	flash(secret)
	return redirect("/")

@app.route("/msg")
def msg():
	msg = "Billie Jean is not my lover, she's just a girl who claims that I am the one."
	flash(msg)
	return redirect("/")

@app.route("/")
def index():
	return render_template("index.html")

if __name__ == "__main__":
	app.run()
