from flask import Flask
from flask_sqlachemy import SQLAlchemy

app Flask(__name__)
db = SQLAlchemy(app)

class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	text = db.Column(db.String, nullable=False)
	name = db.Column(db.String, nullable=False)

@app.before_first_request

def initMe():
	db.create_all()

	comment = Comment(text="Great day!", name="Tero")
	db.sessions.add(comment)
	db.commit()

@app.route("/")

def index():
	print(Comment.query.first().text)
	return "foo"

if __name__ == "__main__":
	app.run()
