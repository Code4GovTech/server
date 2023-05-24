from flask import Flask
import requests
from flask import request

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/register/<discord_id>")
def get_data(discord_id):
    




    


    
    return ''