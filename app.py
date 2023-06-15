from flask import Flask, redirect, render_template
import requests
from flask import request
import dotenv
import os
from db import SupabaseInterface
import json
import urllib, markdown, re

dotenv.load_dotenv(".env")

app = Flask(__name__)
app.config['TESTING']= True
app.config['SECRET_KEY']=os.getenv("FLASK_SESSION_KEY")


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/already_authenticated")
def isAuthenticated():
    return render_template('success.html'), {"Refresh": f'2; url=https://discord.com/channels/{os.getenv("DISCORD_SERVER_ID")}'}

@app.route("/authenticate/<discord_userdata>")
def authenticate(discord_userdata):

    redirect_uri = urllib.parse.quote(f'{os.getenv("HOST")}/register/{discord_userdata}')
    # print(redirect_uri)
    github_auth_url = f'https://github.com/login/oauth/authorize?client_id={os.getenv("GITHUB_CLIENT_ID")}&redirect_uri={redirect_uri}'
    # print(github_auth_url)
    return redirect(github_auth_url)

#this is where github calls back to
@app.route("/register/<discord_userdata>")
def register(discord_userdata):

    #Extrapolate discord data from callback
    #$ sign is being used as separator
    discord_id = discord_userdata

    #Check if the user is registered
    supabase_client = SupabaseInterface()
    # if role == 'mentor':
    #     if supabase_client.mentor_exists(discord_id=discord_id):
    #         print('true')
    #         authenticated_url = f'{os.getenv("HOST")}/already_authenticated'
    #         return redirect(authenticated_url)
    if supabase_client.contributor_exists(discord_id=discord_id):
        # print('true')
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


    user_data = {
        "discord_id": int(discord_id),
        "github_id": github_id,
        "github_url": f"https://github.com/{github_username}",
    }

    #adding to the database
    supabase_client.add_contributor(user_data)
    
    return render_template('success.html'), {"Refresh": f'1; url=https://discord.com/channels/{os.getenv("DISCORD_SERVER_ID")}'}



@app.route("/github/events", methods = ['POST'])
def event_handler():
    supabase_client = SupabaseInterface()
    data = request.json

    if data.get("issue"):
        issue = data["issue"]
        if any(label["name"] == "C4GT Community" for label in issue["labels"] ):
            if not data.get("comment"):
                if data["action"] == "opened":
                    #Event: A new issue was created in some monitored repository
                    markdown_contents = markdownParser(issue["body"])
                    missing_headers = markdownMetadataValidator(markdown_contents)
                    # if missing_headers:
                    #     head = {
                    #         'Accept': 'application/vnd.github+json',
                    #         'Authorization': f'Bearer ghs_oF5E1qRDaNR5qSztdNSUY8fF6xL6ZA2NM4mD'
                    #     }
                    #     url = f'https://api.github.com/repos/OWNER/REPO/issues/{data["issue"]["number"]}/comments'
                    #     requests.post(url, data={"body":"body1"}, json={"body":"body2"}, headers=head)
                        
                    #     return data
                    ticket_points = {
                        "High": 30,
                        "Medium":20,
                        "Low":10,
                        "Unknown":10
                    }
                    ticket_data = {
                        "name":issue["title"],     #name of ticket
                        "product":issue["repository_url"].split('/')[-1],
                        "complexity":markdown_contents["Complexity"],
                        "project_category":markdown_contents["Category"].split(','),
                        "project_sub_category":markdown_contents["Sub Category"].split(','),
                        "reqd_skills":markdown_contents["Tech Skills Needed"],
                        "issue_id":issue["id"],
                        "api_endpoint_url":issue["url"],
                        "url": issue["html_url"],
                        "ticket_points":ticket_points[markdown_contents["Complexity"]]
                    }
                    supabase_client.record_created_ticket(data=ticket_data)
            elif data.get("comment"):
                if data["action"]=="created":
                    #Event: A new comment was created on a C4GT Community ticket
                    supabase_client.add_engagement(data["sender"]["id"])


    supabase_client.add_event_data(data=data)
    return request.json




@app.route("/metrics/discord", methods = ['POST'])
def discord_metrics():
    request_data = json.loads(request.json)
    # print(request_data, type(request_data))
    discord_data = []
    last_measured = request_data["measured_at"]
    metrics = request_data["metrics"]
    for product_name, value in metrics.items():
        data = {
            "product_name" : product_name,
            "mentor_messages" : value['mentor_messages'],
            "contributor_messages": value['contributor_messages']     
        }
        discord_data.append(data)

    supabase_client = SupabaseInterface()
    data = supabase_client.add_discord_metrics(discord_data)
    return data.data

@app.route("/metrics/github", methods = ['POST'])
def github_metrics():
    request_data = json.loads(request.json)
    metrics = request_data["metrics"]
    github_data = []
    for product_name, value in metrics.items():
        data = {
            "product_name" : product_name,
            "open_prs" : value['open_prs'],
            "closed_prs": value['closed_prs'],
            "open_issues": value['open_issues'],
            "closed_issues": value['closed_issues'],
            "number_of_commits": value['number_of_commits'],           
        }
        github_data.append(data)

    supabase_client = SupabaseInterface()
    data = supabase_client.add_github_metrics(github_data)
    return data.data
    
    
