from flask import Flask
from flask import request

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/data/<id>")
def get_data(id):
    data = request.args.get('data')


    
    return f'data:{data}, id:{id}'