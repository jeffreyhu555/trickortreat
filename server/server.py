import sqlite3
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
 'sqlite:///test.db'

db = SQLAlchemy(app)

class House(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	placeid = db.Column(db.String(30))
	address = db.Column(db.String(150))
	lat = db.Column(db.Float())
	lon = db.Column(db.Float())
	notes = db.Column(db.String(5000)) # ### as seperator
	rating = db.Column(db.Float())
	rating_raters = db.Column(db.Integer())
	candies = db.Column(db.String(5000))
	avgcandy = db.Column(db.Float())
	avgcandy_raters = db.Column(db.Integer())
	photos = db.Column(db.String(5000)) # ### as seperator


	def __init__(self, placeid, initial_note, initial_photo, intitial_rating, intitial_candy, initial_candies):
		self.placeid=placeid
		self.address="<NOTCOMPUTED>"
		self.lat=-1
		self.lon=-1
		self.notes=initial_note
		self.rating=intitial_rating if intitial_rating else 0
		self.rating_raters=1
		self.avgcandy=intitial_candy
		self.avgcandy_raters=1 if intitial_candy else 0
		self.photos=initial_photo

class Candy(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	name = db.Column(db.String(30), unique=True)
	tags = db.Column(db.String(5000)) # ### as seperator

	def __init__(self, name, tags):
		self.name=name
		self.tags=tags

@app.route('/api/test')
def hello_world():
	return '{"connected":true}'

if __name__=="__main__":
	app.run()