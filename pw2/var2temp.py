#tehtävä pw2.1

from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")

def index():
	return render_template("temp2-1.html", title="Welcome to Templand!", lorem="lorem ipsum dolor sit amet")

if __name__ == "__main__":
	app.run()
