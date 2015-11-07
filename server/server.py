import sqlite3, time, json, os
from flask import Flask, request
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
	photos = db.Column(db.Strinig(5000))# ### as seperator

	def __init__(self, placeid, initial_note, intitial_rating, intitial_candy, initial_candies):
		self.placeid=placeid
		self.address="<NOTCOMPUTED>"
		self.lat=-1
		self.lon=-1
		self.notes=initial_note
		self.rating=0 if initial_rating==None else intitial_rating
		self.rating_raters=1 if intitial_rating!=None else 0
		self.avgcandy=0 if initial_candy==None else intitial_candy
		self.avgcandy_raters=1 if intitial_candy!=None else 0
		self.candies=initial_candies
		self.photos=""

class Candy(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	name = db.Column(db.String(30), unique=True)
	tags = db.Column(db.String(5000)) # ### as seperator

	def __init__(self, name, tags):
		self.name=name
		self.tags=tags

lambda FAIL(code, data=None): json.dumps({"success":False, "error":code, "info":data})

def reduce(l):
	c=[]
	for i in l:
		if i not in c: c.append(i)
	return c

@app.route('/upload', methods=['POST', 'GET'])
def api_upload():
	if request.method!="POST": return FAIL("wrong_method")
	if "?" not in request.url: return FAIL("no_placeid")
	if not request.files or 'image' not in request.files: return FAIL("no_attachment")

	placeid=request.url.split("?",1)[1]
	f=request.files['image']
	ext=f.filename.split(".",1)[1]

	if ext not in ["png","jpg","jpeg","gif"]: return FAIL("invalid_extention")

	record=db.session.query(House).filter_by(placeid=placeid)

	if not record: return FAIL("no_such_placeid")

	fname=placeid+str(len(record.images.split("###"))-1)+ext
	record.images+=fname+"###"
	db.session.commit()
	f.save("static/uploads/"+fname)

	return json.dumps({"success":True})

@app.route('/submit', methods=['POST', 'GET'])
def api_submit():
	if request.method!="POST": return FAIL("wrong_method")
	if not request.data: return FAIL("no_data")
	try:
		data=json.loads(request.data)
	except json.decoder.JSONDecodeError as e:
		return FAIL("invalid_data", str(e))

	if "placeid" not in data: FAIL("no_placeid")
	if data["placeid"]=="": FAIL("invalid_placeid")

	record=session.query(House).filter_by(placeid=data["placeid"])

	if not record:
		record=House(data["placeid"], data.get("note",""), data.get("rating"), data.get("candy"), "###".join(data.get("candies"))+("" if "candies" in data else "###"))
		db.session.add(record)
	else:
		if "note" in data:
			record.notes+=data["note"].replace("###","##")+"###"
		if "rating" in data:
			record.rating+=data["rating"] #TODO: Real calculation

	db.session.commit()






@app.route('/test')
def api_test():
	return json.dumps({"success":True})



if __name__=="__main__":
	app.run()