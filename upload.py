#
#  NOTE: A NUMBER OF EDITS STILL NEED TO BE MADE FOR THIS 
#  allowed_file must be made to allow files as we want
#  file saving must be altered to save images as not onle .jpeg files
#  ALLOWED_EXTENSIONS should have all the extensions we are allowing
#  If there is a better way to generate file names, use it
#
import math
import time
from flask import Flask, request, redirect, url_for
app = Flask(__name__)
ALLOWED_EXTENSIONS = set(['jpeg'])
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
fcount = 0 # This counts the number of files (for making file name) from curre$
curtime = time.time() # Current time
def allowed_file(filename):
        return '.' in filename and \
                filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload():
        global curtime
        global fcount
        if request.method == 'POST':
                if (int(curtime) != int(time.time())): # Restarting on file na$
                        curtime = time.time()
                        fcount = 0
                fcount += 1
                fname = str(int(curtime))+str(fcount)
                file = request.files['dog']
                if allowed_file(file.filename):
                    file.save('static/uploads/'+fname+'.jpeg')
                    return redirect('static/uploads/'+fname+'.jpeg')
        return

if __name__ == '__main__':
    app.run()

