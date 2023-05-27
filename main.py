from flask import Flask, redirect, render_template
import requests
from flask import request
import dotenv
import os
from db import SupabaseInterface

dotenv.load_dotenv(".env")

app = Flask(__name__)
app.config['TESTING']= True
app.config['SECRET_KEY']=os.getenv("FLASK_SESSION_KEY")

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/already_authenticated")
def isAuthenticated():
    return render_template('success.html'), {"Refresh": f'1; url=https://discord.com/channels/{os.getenv("DISCORD_SERVER_ID")}'}

@app.route("/authenticate/<discord_userdata>")
def authenticate(discord_userdata):

    redirect_uri = f'{os.getenv("HOST")}/register/{discord_userdata}'
    github_auth_url = f'https://github.com/login/oauth/authorize?client_id={os.getenv("GITHUB_CLIENT_ID")}&redirect_uri={redirect_uri}'
    return redirect(github_auth_url)

#this is where github calls back to
@app.route("/register/<discord_userdata>")
def register(discord_userdata):
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    #Extrapolate discord data from callback
    #$ sign is being used as separator
    [discord_id, discord_username, role] = discord_userdata.split('$')

    #Check if the user is registered
    supabase_client = SupabaseInterface(url=url, key=key)
    if supabase_client.user_exists(discord_id=discord_id):
        print('true')
        authenticated_url = f'{os.getenv("HOST")}/already_authenticated'
        return redirect(authenticated_url)

    #get github ID
    github_url_for_access_token = 'https://github.com/login/oauth/access_token'
    data = {
        "client_id": os.getenv("GITHUB_CLIENT_ID"),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
        "code": request.args.get("code")
    }
    header = {
        "Accept":"application/json"
    }
    r = requests.post(github_url_for_access_token, data=data, headers=header)
    auth_token = r.json()["access_token"]
    user = requests.get("https://api.github.com/user", headers={
        "Authorization": f"Bearer {auth_token}"
    })
    print(user.json())

    github_id = user.json()["id"]
    github_username = user.json()["login"]


    #adding to the database
    supabase_client.add_user({
        "discord_id": int(discord_id),
        "github_id": github_id,
        "github_url": f"https://github.com/{github_username}",
        "discord_username": discord_username,
        "role": role
    })

    

    return render_template('success.html'), {"Refresh": f'1; url=https://discord.com/channels/{os.getenv("DISCORD_SERVER_ID")}'}