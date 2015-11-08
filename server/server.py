import sqlite3, time, json, os, sqlalchemy
from flask import Flask, request, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from math import sin, cos, sqrt, atan2, radians

def calc_dist(lat1, lon1, lat2, lon2):
	R = 3959.0

	lat1 = radians(lat1)
	lon1 = radians(lon1)
	lat2 = radians(lat2)
	lon2 = radians(lon2)

	dlon = lon2 - lon1
	dlat = lat2 - lat1

	a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
	c = 2 * atan2(sqrt(a), sqrt(1 - a))

	return R * c

candy_db={
	"snickers":["peanuts", "chocolate", "caramel"],
	"twizzlers":["licorice"],
	"hersheys":["chocolate"],
	"full size hersheys":["chocolate", "Hersheys"]
}

app = Flask(__name__)
app.debug=1
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

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

	def __init__(self, placeid, address, lat, lon, initial_note, initial_rating, initial_candy, initial_candies):
		self.placeid=placeid
		self.address=address
		self.lat=lat
		self.lon=lon
		self.notes=initial_note
		self.rating=0 if initial_rating==None else initial_rating
		self.rating_raters=1 if initial_rating!=None else 0
		self.avgcandy=0 if initial_candy==None else initial_candy
		self.avgcandy_raters=1 if initial_candy!=None else 0
		self.candies=initial_candies
		self.visits=1
		self.photos="[]"

def FAIL(code, data=None): return json.dumps({"success":False, "error":code, "info":data})

def deduplicate(l):
	c=[]
	for i in l:
		if i not in c: c.append(i)
	return c

def castdefault(d, k, type, default):
	if k not in d: return default
	if d[k]=="": return default
	return type(d[k])

@app.route('/upload', methods=['POST', 'GET'])
def api_upload():
	if request.method!="POST": return FAIL("wrong_method")
	if "?" not in request.url: return FAIL("no_placeid")
	print(request.files)
	if not request.files or 'image' not in request.files: return FAIL("no_attachment")

	placeid=request.url.split("?",1)[1].split("&")[0]
	f=request.files['image']
	ext=f.filename.split(".",1)[1]

	if ext not in ["png","jpg","jpeg","gif"]: return FAIL("invalid_extention")

	try:
		record=House.query.filter_by(placeid=placeid).one()
	except qlalchemy.orm.exc.NoResultFound:
		return FAIL("no_such_placeid")

	rp=eval(record.photos)
	fname=placeid+str(len(rp))+"."+ext
	rp.append(fname)
	record.photos=repr(rp)
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
			data["lat"]=castdefault(data, "lat", float, -1)
			data["lon"]=castdefault(data, "lon", float, -1)
			data["rating"]=castdefault(data, "rating", int, -1)
			data["candy"]=castdefault(data, "candy", int, -1)
		except (json.decoder.JSONDecodeError, ValueError) as e:
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
			print(c)
			print(data)
			record=House(data["placeid"], data["address"], data["lat"], data["lon"], repr([data["note"]] if data.get("note","")!="" else []), data["rating"], data["candy"], repr(c))
			db.session.add(record)
		else:
			if "note" in data and data["note"]!="":
				n=eval(record.notes)
				n.append(data["note"])
				record.notes=repr(n)
			if data["rating"]!=-1:
				record.rating+=float(data["rating"]) #TODO: Real calculation
				record.rating_raters+=1
			if data["candy"]!=-1:
				record.avgcandy+=float(data["candy"]) #TODO: Real calculation
				record.avgcandy_raters+=1
			if "candies" in data and data["candies"]!=[""]:
				c=eval(record.candies)
				for e in data["candies"]:
					if e: c.append(e)
				record.candies=repr(deduplicate(c))
			if record.lat==-1:
				record.lat=data["lat"]
				record.lon=data["lon"]
			record.visits+=1

		db.session.commit()
		print("yay")
		return json.dumps({"success":True})
	except json.decoder.JSONDecodeError as e:
		return FAIL("unknown_error", str(e))

@app.route('/request', methods=['POST', 'GET'])
def api_request():
	if request.method!="POST": return FAIL("wrong_method")
	if not request.data: return FAIL("no_data")
	request.data=request.data.decode("utf-8")
	try:
		data=json.loads(str(request.data))
		data["lat"]=castdefault(data, "lat", float, -1)
		data["lon"]=castdefault(data, "lon", float, -1)
		data["dist"]=castdefault(data, "dist", float, -1)
		data["rating"]=castdefault(data, "rating", float, -1)
		data["candy"]=castdefault(data, "candy", float, -1)
		data["required"]=data["required"] if data["required"]!=[""] else []
		data["disallowed"]=data["disallowed"] if data["disallowed"]!=[""] else []
	except (json.decoder.JSONDecodeError, ValueError) as e:
		return FAIL("invalid_data", str(e))

	name={"houses":[], "success":True}

	for row in House.query.all():
		if data["rating"]!=-1:
			if (row.rating/row.rating_raters if row.rating_raters else -1)<=data["rating"]:
				continue

		if data["candy"]!=-1:
			if (row.avgcandy/row.avgcandy_raters if row.avgcandy_raters else -1)<=data["candy"]:
				continue

		if data["dist"]!=-1:
			if calc_dist(data["lat"], data["lon"], row.lat, row.lon)>data["dist"]:
				continue

		tags=[]
		for candy in eval(row.candies):
			tags.extend(candy_db.get(candy.lower(), [candy.lower()]))

		good=True
		for i in data["required"]:
			if i not in tags:
				good=False
		if not good: continue

		good=True
		for i in data["disallowed"]:
			if i in tags: 
				good=False
		if not good: continue

		name["houses"].append({
			"placeid":row.placeid,
			"address":row.address,
			"lat":row.lat,
			"lon":row.lon,
			"calc_rating":row.rating/row.rating_raters if row.rating_raters else -1,
			"calc_avgcandy":row.avgcandy/row.avgcandy_raters if row.avgcandy_raters else -1,
			"rating":row.rating,
			"avgcandy":row.avgcandy,
			"avgcandy_raters":row.avgcandy_raters,
			"rating_raters":row.rating_raters,
			"id":row.id,
			"candies":eval(row.candies),
			"visits":row.visits,
			"notes":eval(row.notes),
			"photos":eval(row.photos)
		})

	return json.dumps(name)

@app.route('/debugrequest', methods=['POST', 'GET'])
def api_debugrequest():
	name={"houses":[], "success":True}

	for row in House.query.all():
		tags=[]
		for candy in eval(row.candies):
			tags.extend(candy_db.get(candy.lower(), [candy.lower()]))
		name["houses"].append({
			"placeid":row.placeid,
			"address":row.address,
			"lat":row.lat,
			"lon":row.lon,
			"calc_rating":row.rating/row.rating_raters if row.rating_raters else -1,
			"calc_avgcandy":row.avgcandy/row.avgcandy_raters if row.avgcandy_raters else -1,
			"rating":row.rating,
			"avgcandy":row.avgcandy,
			"avgcandy_raters":row.avgcandy_raters,
			"rating_raters":row.rating_raters,
			"id":row.id,
			"candies":eval(row.candies),
			"visits":row.visits,
			"notes":eval(row.notes),
			"photos":eval(row.photos),
			"tags":tags
		})

	return json.dumps(name)

@app.route('/test')
def api_test():
	return json.dumps({"success":True})

@app.route('/', methods=['POST', 'GET'])
def root():
	return redirect("/static/client/index.html")

if __name__=="__main__":
	app.run()