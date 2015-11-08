import math
import time
from flask import Flask, request, redirect, url_for
app = Flask(__name__)
ALLOWED_EXTENSIONS = set(['jpeg'])
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
fcount = 0 # This counts the number of files (for making file name) from current one
curtime = time.time() # Current time
def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
def checkpid(placeid): # Returns false if placeid invalid, otherwise true
	return placeid
def addphoto(placeid, filename): # Takes placeid of a photo and filename and adds photo to database matching placeid
	return
@app.route('/')
def hello_world():
    return 'Hello World!'
@app.route('/upload', methods=['GET', 'POST'])
def upload():
	global curtime
	global fcount
	if request.method == 'POST':
		if (int(curtime) != int(time.time())): # Restarting on file names
			curtime = time.time()
			fcount = 0
		fcount += 1
		file = request.files['dog']
		placeid = request.form['placeid']
		if allowed_file(file.filename) and checkpid(placeid):
	                fname = str(int(curtime))+str(fcount)+'.'+file.filename.rsplit('.', 1)[1]
			file.save('static/uploads/'+fname)
			addphoto(placeid, fname)
			return redirect('static/uploads/'+fname)
		elif checkpid(placeid):
			return "Error: Forbidden filename"
		else:
			return "Error: Invalid place ID"
	return

if __name__ == '__main__':
    app.run()
