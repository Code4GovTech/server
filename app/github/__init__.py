from quart import Blueprint, request
import aiohttp

import sys, os

from utils.db import SupabaseInterface
from events.ticketEventHandler import TicketEventHandler
from githubdatapipeline.issues.destination import recordIssue
from installations import installations

github = Blueprint(
    'github',
    __name__,
    url_prefix='/github')

github.register_blueprint(installations)

async def get_url(url):
    headers = {
            'Authorization': f'Bearer {os.getenv("GithubPAT")}',
            'Accept': 'application/vnd.github.machine-man-preview+json'  # Required for accessing GitHub app APIs
            }
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                response.raise_for_status()  # Raise an exception if the response status is not 2xx (successful)
                return await response.json()
    except aiohttp.ClientError as e:
        print(f"An error occurred while fetching the URL: {e}")
        return None

@github.route("/events", methods = ['POST'])
async def event_handler():
    eventType = request.headers['X-GitHub-Event']

    supabase_client = SupabaseInterface()

    # if request.headers["X-GitHub-Event"] == 'installation' or request.headers["X-GitHub-Event"] == 'installation_repositories':
    #     data = await request.json 
    #     if data.get("action")=="created" or data.get("action")=="added":
    #         # New installation created
    #         repositories = data.get("repositories") if data.get("repositories") else data.get("repositories_added")
    #         for repository in repositories:
    #             owner, repository = repository["full_name"].split('/')
    #             issues = await fetch_github_issues_from_repo(owner, repository)
    #             for issue in issues:
    #                 await TicketEventHandler().onTicketCreate({'issue': issue})
        #on installation event

    data = await request.json
    print(data, file = sys.stderr)
    # supabase_client.add_event_data(data=data)
    if data.get("issue"):
        issue = data["issue"]
        try:
            recordIssue(issue)
        except Exception as e:
            print(e)
        if supabase_client.checkUnlisted(issue["id"]):
            supabase_client.deleteUnlistedTicket(issue["id"])
        await TicketEventHandler().onTicketCreate(data)
        if supabase_client.checkIsTicket(issue["id"]):
            await TicketEventHandler().onTicketEdit(data)
            if data["action"] == "closed":
                await TicketEventHandler().onTicketClose(data)
    if data.get("installation") and data["installation"].get("account"):
        # if data["action"] not in ["deleted", "suspend"]:
        await TicketEventHandler().updateInstallation(data.get("installation"))
    
    # if data.

    return data

