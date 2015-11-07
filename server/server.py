import sqlite3
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
 'mysql://602p:'+open("dbpassword",'r').read()+'@602p.mysql.pythonanywhere-services.com/602p$trickortreat'

db = SQLAlchemy(app)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	email = db.Column(db.String(120), unique=True)

	def __init__(self, username, email):
		self.username = username
		self.email = email

	def __repr__(self):
		return '<User %r>' % self.username

@app.route('/api/test')
def hello_world():
	return '{"connected":true}'

if __name__=="__main__":
	app.run()