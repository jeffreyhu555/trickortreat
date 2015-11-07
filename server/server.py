from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
 'mysql://602p:'+open("dbpassword",'r').read()+'@602p.mysql.pythonanywhere-services.com/602p$trickortreat'

@app.route('/api/test')
def hello_world():
    return '{"connected":true}'

if __name__=="__main__":
	app.run() 