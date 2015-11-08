import sqlite3, time, json, os, sqlalchemy
from flask import Flask, request
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.debug=1
app.config['SQLALCHEMY_DATABASE_URI'] =\
 'sqlite:///test.db'

db = SQLAlchemy(app)

class House(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	placeid = db.Column(db.String(30))
	address = db.Column(db.String(150))
	lat = db.Column(db.Float())
	lon = db.Column(db.Float())
	notes = db.Column(db.String(5000))
	rating = db.Column(db.Float())
	rating_raters = db.Column(db.Integer())
	candies = db.Column(db.String(5000))
	avgcandy = db.Column(db.Float())
	avgcandy_raters = db.Column(db.Integer())
	photos = db.Column(db.String(5000))
	visits = db.Column(db.Integer())

	def __init__(self, placeid, initial_note, initial_rating, initial_candy, initial_candies):
		self.placeid=placeid
		self.address="<NOTCOMPUTED>"
		self.lat=-1
		self.lon=-1
		self.notes=initial_note
		self.rating=0 if initial_rating==None else initial_rating
		self.rating_raters=1 if initial_rating!=None else 0
		self.avgcandy=0 if initial_candy==None else initial_candy
		self.avgcandy_raters=1 if initial_candy!=None else 0
		self.candies=initial_candies
		self.visits=1
		self.photos=""

class Candy(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	name = db.Column(db.String(30), unique=True)
	tags = db.Column(db.String(5000)) # ### as seperator

	def __init__(self, name, tags):
		self.name=name
		self.tags=tags

def FAIL(code, data=None): return json.dumps({"success":False, "error":code, "info":data})

def deduplicate(l):
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

	record=House.query.filter_by(placeid=placeid).one()

	if not record: return FAIL("no_such_placeid")

	fname=placeid+str(len(record.images.split("###"))-1)+ext
	record.images+=fname+"###"
	db.session.commit()
	f.save("static/uploads/"+fname)

	return json.dumps({"success":True})

@app.route('/submit', methods=['POST', 'GET'])
def api_submit():
	try:
		if request.method!="POST": return FAIL("wrong_method")
		if not request.data: return FAIL("no_data")
		request.data=request.data.decode("utf-8")
		try:
			data=json.loads(str(request.data))
		except json.decoder.JSONDecodeError as e:
			return FAIL("invalid_data", str(e))

		if "placeid" not in data: return FAIL("no_placeid")
		if data["placeid"]=="": return FAIL("invalid_placeid")

		try:
			record=House.query.filter_by(placeid=data["placeid"]).one()
		except sqlalchemy.orm.exc.NoResultFound:
			record=None

		if not record:
			c=[]
			for i in data.get("candies",[]):
				if i: c.append(i)
			record=House(data["placeid"], repr([data["note"]] if data.get("note","")!="" else []), data.get("rating"), data.get("candy"), repr(c))
			db.session.add(record)
		else:
			if "note" in data and data["note"]!="":
				n=eval(record.notes)
				n.append(data["note"])
				record.notes=repr(n)
			if "rating" in data:
				record.rating+=float(data["rating"]) #TODO: Real calculation
				record.rating_raters+=1
			if "candy" in data:
				record.avgcandy+=float(data["candy"]) #TODO: Real calculation
				record.avgcandy_raters+=1
			if "candies" in data and data["candies"]!=[""]:
				c=eval(record.candies)
				for e in data["candies"]:
					if e: c.append(e)
				record.candies=repr(deduplicate(c))
			record.visits+=1

		db.session.commit()
		print("yay")
		return json.dumps({"success":True})
	except json.decoder.JSONDecodeError as e:
		return FAIL("unknown_error", str(e))

@app.route('/request', methods=['POST', 'GET'])
def api_request():
	# if not request.data: return FAIL("no_data")
	# try:
	# 	data=json.loads(request.data)
	# except json.decoder.JSONDecodeError as e:
	# 	return FAIL("invalid_data", str(e))

	try:
		name={"houses":[], "success":True}

		for row in House.query.all():
			name["houses"].append({
				"placeid":row.placeid,
				"address":row.address,
				"lat":row.lat,
				"lon":row.lon,
				"rating":row.rating/row.rating_raters,
				"avgcandy":row.avgcandy/row.avgcandy_raters,
				"candies":eval(row.candies),
				"visits":row.visits,
				"notes":eval(row.notes)
			})

		return json.dumps(name)
	except BaseException as e:
		return FAIL("unknown_error", str(e))

@app.route('/test')
def api_test():
	return json.dumps({"success":True})

if __name__=="__main__":
	app.run()