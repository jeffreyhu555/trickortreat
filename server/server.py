
# A very simple Flask Hello World app for you to get started with...

from flask import Flask

app = Flask(__name__)

@app.route('/api/test')
def hello_world():
    return '{"connected":true}'