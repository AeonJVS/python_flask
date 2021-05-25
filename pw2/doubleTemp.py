#tehtävä pw2.2 ja pw2.3

from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")

def index():
	return render_template("base.html", name = "Shiva", relationship = "Destroyer", sibling = "Worlds")

@app.route("/ares")
def brother():
	return render_template("ares.html", name = "Julius Caesar", relationship = "Imperator ", sibling="Rome")

@app.route("/eris")
def sister():
	return render_template("eris.html", name = "Nobody", relationship = "ideal", sibling = "no one")

@app.route("/victories")
def victories():
	victoriesOfCaesar = ["Battle of Bibracte","Battle of Vosges","Battle of the Sabis River","Battle of Morbihan Gulf","The Gallic Wars","Battle at Gergovia","Battle at Lutetia Parisiorum","Battle at Alesia"]
	return render_template("victories.html", victoriesOfCaesar=victoriesOfCaesar, name = "Julius Caesar", relationship = "Victor", sibling = "Many battles")

if __name__ == "__main__":
	app.run()
