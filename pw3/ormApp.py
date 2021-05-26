from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

class Greatmen(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)

@app.before_first_request
def initMe():
	db.create_all()

	greatman1 = Greatmen(name="Caracalla")
	greatman2 = Greatmen(name="Nero")
	greatman3 = Greatmen(name="Caligula")

	db.session.add_all([greatman1, greatman2, greatman3])
	db.session.commit()

@app.route("/")

def index():
	print(Greatmen.query.first().name)
	return render_template("index.html", greatman=Greatmen.query.first(), greatmen=Greatmen.query.all())

if __name__ == "__main__":
	app.run()
