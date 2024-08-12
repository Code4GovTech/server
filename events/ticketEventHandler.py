# Tickets are created, edited and deleted
# Comments are created edited and deleted

import aiohttp
import os, sys, datetime, json
from utils.db import SupabaseInterface
from utils.markdown_handler import MarkdownHeaders
from utils.github_api import GithubAPI
from utils.jwt_generator import GenerateJWT
from aiographql.client import GraphQLClient, GraphQLRequest
from events.ticketFeedbackHandler import TicketFeedbackHandler
# from githubdatapipeline.issues.processor import closing_pr
import postgrest
from githubdatapipeline.issues.processor import returnConnectedPRs
from fuzzywuzzy import fuzz

def matchProduct(enteredProductName):
    products = [
    "ABDM",
    "AI Tools",
    "Avni",
    "Bahmni",
    "Beckn DSEP",
    "Beckn",
    "CARE",
    "CORD Network",
    "cQube",
    "DDP",
    "DevOps Pipeline",
    "DIGIT",
    "DIKSHA",
    "Doc Generator",
    "Dalgo",
    "Farmstack",
    "Glific",
    "Health Claims Exchange",
    "Karmayogi",
    "ODK Extension Collection",
    "Quiz Creator",
    "QuML player for Manage learn",
    "Solve Ninja Chatbot",
    "Sunbird DevOps",
    "Sunbird ED",
    "Sunbird inQuiry",
    "Sunbird Knowlg",
    "Sunbird Lern",
    "Sunbird Obsrv",
    "Sunbird RC",
    "Sunbird Saral",
    "SL-Library",
    "Sunbird UCI",
    "Template Creation Portal",
    "Text2SQL",
    "TrustBot and POSHpal",
    "TrustIn",
    "Unnati",
    "WarpSQL",
    "Workflow",
    "Yaus",
    "C4GT Tech"
]
    matchingProduct = None
    for product in products:
        if fuzz.ratio(enteredProductName.lower(), product.lower())>80:
            matchingProduct = product
        if fuzz.partial_ratio(enteredProductName.lower(), product.lower())>80:
            matchingProduct = product
        if fuzz.token_sort_ratio(enteredProductName.lower(), product.lower())>80:
            matchingProduct = product
        if fuzz.token_set_ratio(enteredProductName.lower(), product.lower())>80:
            matchingProduct = product
    return matchingProduct



async def send_message(ticket_data):
    discord_channels = SupabaseInterface().readAll("discord_channels")
    products = SupabaseInterface().readAll("product")

    url = None
    # for product in products:
    #     if product["name"].lower() == message["product"].lower():
    #         for channel in discord_channels:
    #             if channel["channel_id"] == product["channel"]:
    #                 if channel["should_notify"]:
    #                     url = channel["webhook"]

    webhook_url = 'https://discord.com/api/webhooks/1126709789876043786/TF_IdCbooRo7_Y3xLzwSExdpvyFcoUGzxBGS_oqCH7JcVq0mzYbu6Av0dbVWjgqYUoNM'
    message = f'''Hey! 
A new project has been listed under {ticket_data["product"]} 💻 
🗃️ Project Link - {ticket_data["url"]}
📈 Complexity - {ticket_data["complexity"]}
⚒️ Tech Skills Required - {ticket_data["reqd_skills"]}
📄 Category - {ticket_data["project_category"]}
🏅 Points - {ticket_data["ticket_points"]}
Check out this project, get coding and earn more DPG points🥳'''
    headers = {
        "Content-Type": 'application/json'
    }

    payload = {
        'content': message
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(webhook_url,headers=headers, data=json.dumps(payload)) as response:
            if response.status == 204:
                print('Message sent successfully')
            else:
                print(f'Failed to send message. Status code: {response}')
        
        if url:
            async with session.post(url,headers=headers, data=json.dumps(payload)) as response:
                if response.status == 204:
                    print('Message sent successfully')
                else:
                    print(f'Failed to send message. Status code: {response}')

async def get_pull_request(owner, repo, number):
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {os.getenv("GithubPAT")}'
    }
    url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{number}'
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None


class TicketEventHandler:
    def __init__(self):
        self.supabase_client = SupabaseInterface()
        self.ticket_points = {
                        "hard":30,
                        "easy":10,
                        "high": 30,
                        "medium":20,
                        "low":10,
                        "unknown":10,
                        "beginner": 5
                    }
        
        self.complexity_synonyms = {
            "easy": "Low",
            "low": "Low",
            "medium": "Medium",
            "hard": "High",
            "high": "High",
            "complex": "High",
            "beginner":"Beginner"

        }
        return
    
    async def onTicketCreate(self, eventData):
        issue = eventData["issue"]
        print('ticket creation called')
        if any(label["name"].lower() in ["c4gt community".lower(), "dmp 2024"] for label in issue["labels"] ):
            if any(label["name"].lower() == "c4gt community" for label in issue["labels"]):
                ticketType = "ccbp"
            else:
                ticketType = "dmp"
            markdown_contents = MarkdownHeaders().flattenAndParse(issue["body"])
            # print(markdown_contents, file=sys.stderr)
            ticket_data = {
                        "name":issue["title"],     #name of ticket
                        # "product":matchProduct(markdown_contents["Product Name"]) if markdown_contents.get("Product Name") else matchProduct(markdown_contents["Product"]) if markdown_contents.get("Product") else None,
                        "product":markdown_contents["Product Name"] if markdown_contents.get("Product Name") else markdown_contents["Product"] if markdown_contents.get("Product") else None,
                        "complexity":self.complexity_synonyms[markdown_contents["Complexity"].lower()] if markdown_contents.get("Complexity") else None ,
                        "project_category":markdown_contents["Category"].split(',') if markdown_contents.get("Category") else None,
                        "project_sub_category":markdown_contents["Sub Category"].split(',') if markdown_contents.get("Sub Category") else None,
                        "reqd_skills":[skill for skill in markdown_contents["Tech Skills Needed"].split(',')] if markdown_contents.get("Tech Skills Needed") else None,
                        "issue_id":issue["id"],
                        "status": issue["state"],
                        "api_endpoint_url":issue["url"],
                        "url": issue["html_url"],
                        "organization": markdown_contents["Organisation Name"] if markdown_contents.get("Organisation Name") else None,
                        "ticket_points":self.ticket_points[markdown_contents["Complexity"].lower()] if markdown_contents.get("Complexity") and markdown_contents.get("Complexity").lower() in self.ticket_points.keys()  else 10,
                        "mentors": [github_handle for github_handle in markdown_contents["Mentor(s)"].split(' ')] if markdown_contents.get("Mentor(s)") else None
                    }
            # print(ticket_data, file=sys.stderr)
            if ticketType == "ccbp" and ticket_data["product"] and ticket_data["complexity"] and ticket_data["reqd_skills"] and ticket_data["mentors"] and ticket_data["project_category"]:
                if not self.supabase_client.checkIsTicket(ticket_data["issue_id"]):
                    await send_message(ticket_data)
                self.supabase_client.record_created_ticket(data=ticket_data)
            elif ticketType == "dmp":
                if not self.supabase_client.checkIsDMPTicket(ticket_data["issue_id"]):
                    await send_message(ticket_data)
                self.supabase_client.recordCreatedDMPTicket(data=ticket_data)
            else:
                print("TICKET NOT ADDED", ticket_data, file=sys.stderr)
                self.supabase_client.insert("unlisted_tickets", ticket_data)

            if TicketFeedbackHandler().evaluateDict(markdown_contents) and ticketType == "ccbp":
                url_components = issue["url"].split('/')
                issue_number = url_components[-1]
                repo = url_components[-3]
                owner = url_components[-4]
                try:
                    print('recording comments in Tickets creation')
                    SupabaseInterface().recordComment({
                            "issue_id":issue["id"],
                            "updated_at": datetime.datetime.utcnow().isoformat()
                        })
                    print('starting comment creation in ticket create')
                    comment = await TicketFeedbackHandler().createComment(owner, repo, issue_number, markdown_contents)
                    if comment:
                        SupabaseInterface().updateComment({
                            "api_url":comment["url"],
                            "comment_id":comment["id"],
                            "issue_id":issue["id"],
                            "updated_at": datetime.datetime.utcnow().isoformat()
                        })
                except Exception as e:
                    print("Issue already commented ", e)
        return eventData

    async def onTicketEdit(self, eventData):
        issue = eventData["issue"]
        print('edit ticket called')
        if eventData["action"] == "unlabeled":
            if (not issue["labels"]) or (not any(label["name"].lower() in ["C4GT Community".lower(), "dmp 2024"] for label in issue["labels"] )):
                # Delete Ticket
                self.supabase_client.deleteTicket(issue["id"])
                return
        if any(label["name"].lower() == "c4gt community" for label in issue["labels"]):
            ticketType = "ccbp"
        else:
            ticketType = "dmp"
        markdown_contents = MarkdownHeaders().flattenAndParse(issue["body"])
        print("MARKDOWN", markdown_contents, file=sys.stderr )
        ticket_data = {
                        "name":issue["title"],     #name of ticket
                        "product":markdown_contents["Product Name"] if markdown_contents.get("Product Name") else markdown_contents["Product"] if markdown_contents.get("Product") else None,
                        "complexity":self.complexity_synonyms[markdown_contents["Complexity"].lower()] if markdown_contents.get("Complexity") else None ,
                        "project_category":markdown_contents["Category"].split(',') if markdown_contents.get("Category") else None,
                        "project_sub_category":markdown_contents["Sub Category"].split(',') if markdown_contents.get("Sub Category") else None,
                        "reqd_skills":[skill for skill in markdown_contents["Tech Skills Needed"].split(',')] if markdown_contents.get("Tech Skills Needed") else None,
                        "issue_id":issue["id"],
                        "status": issue["state"],
                        "api_endpoint_url":issue["url"],
                        "url": issue["html_url"],
                        "organization": markdown_contents["Organisation Name"] if markdown_contents.get("Organisation Name") else None,
                        "ticket_points":self.ticket_points[markdown_contents["Complexity"].lower()] if markdown_contents.get("Complexity") and markdown_contents.get("Complexity").lower() in self.ticket_points.keys()  else 10,
                        "mentors": [github_handle for github_handle in markdown_contents["Mentor(s)"].split(' ')] if markdown_contents.get("Mentor(s)") else None
                    }
        # print("TICKET", ticket_data, file=sys.stderr)
        if ticketType == "ccbp":
            self.supabase_client.update_recorded_ticket(data=ticket_data)
        elif ticketType == "dmp":
            self.supabase_client.updateRecordedDMPTicket(data=ticket_data)

        if SupabaseInterface().commentExists(issue["id"]) and ticketType=="ccbp":
            url_components = issue["url"].split('/')
            repo = url_components[-3]
            owner = url_components[-4]
            comment_id = SupabaseInterface().readCommentData(issue["id"])[0]["comment_id"]
            if TicketFeedbackHandler().evaluateDict(markdown_contents):
                comment = await TicketFeedbackHandler().updateComment(owner, repo, comment_id, markdown_contents)
                if comment:
                    SupabaseInterface().updateComment({
                        "updated_at": datetime.datetime.utcnow().isoformat(),
                        "issue_id": issue["id"]
                    })
            else:
                try:
                    comment = await TicketFeedbackHandler().deleteComment(owner, repo, comment_id)
                    print(f"Print Delete Task,{comment}", file=sys.stderr)
                    print(SupabaseInterface().deleteComment(issue["id"]))
                except:
                    print("Error in deletion")
        elif ticketType=="ccbp":
            if TicketFeedbackHandler().evaluateDict(markdown_contents):
                url_components = issue["url"].split('/')
                issue_number = url_components[-1]
                repo = url_components[-3]
                owner = url_components[-4]
                try:
                    print('inserting comments data in ticket edit')
                    SupabaseInterface().recordComment({
                            "issue_id":issue["id"],
                            "updated_at": datetime.datetime.utcnow().isoformat()
                        })
                    print('starting comment creation in ticket edit')
                    comment = await TicketFeedbackHandler().createComment(owner, repo, issue_number, markdown_contents)
                    if comment:
                        SupabaseInterface().updateComment({
                            "api_url":comment["url"],
                            "comment_id":comment["id"],
                            "issue_id":issue["id"],
                            "updated_at": datetime.datetime.utcnow().isoformat()
                        })
                except Exception as e:
                    print("Issue already commented ", e)

        return eventData
    
    async def onTicketClose(self, eventData):
        issue = eventData["issue"]
        [repo, owner, issue_number] = [issue["url"].split('/')[-3],issue["url"].split('/')[-4],issue["url"].split('/')[-1]]
        pullData = await returnConnectedPRs(issue)

        print("PULL REQUEST",pullData, file = sys.stderr)
        self.supabase_client.addPr(pullData, issue["id"])
                    
        return
    
    async def updateInstallation(self, installation):
        async def get_repositories(installation):
            repositories_url = f'https://api.github.com/installation/repositories'
            token = await GithubAPI().authenticate_app_as_installation(installation["account"]["login"])
            headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github.machine-man-preview+json'  # Required for accessing GitHub app APIs
        }

            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(repositories_url) as response:
                    # print(await response.json(), file=sys.stderr)
                    if response.status == 200:
                        data = await response.json()
                        
                        return data["repositories"]
        async def get_issues(repository):
                        # print(repository, file=sys.stderr)
            url = repository["url"]
            issue_url = url+"/issues"
            headers = {
            'Authorization': f'Bearer {os.getenv("GithubPAT")}',
            'Accept': 'application/vnd.github.machine-man-preview+json'  # Required for accessing GitHub app APIs
            }
            

            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(issue_url) as response:
                    if response.status == 200:
                        issues = await response.json()
                        # print(comments, file=sys.stderr)
                        return issues
        
        repositories = await get_repositories(installation)
        for repository in repositories:
            issues = await get_issues(repository)
            for issue in issues:
                await self.onTicketCreate({"issue":issue})



             

        
        return installation
    
    async def bot_comments(self):
                    # headers = {
                    #     'Authorization': f'Bearer {token}',
                    #     'Accept': 'application/vnd.github.machine-man-preview+json'  # Required for accessing GitHub app APIs
                    # }

                    async def get_installations():
                        token = GenerateJWT().__call__()
                        headers = {
                        'Authorization': f'Bearer {token}',
                        'Accept': 'application/vnd.github.machine-man-preview+json'  # Required for accessing GitHub app APIs
                    }
                        installations_url = 'https://api.github.com/app/installations'

                        async with aiohttp.ClientSession(headers=headers) as session:
                            async with session.get(installations_url) as response:
                                if response.status == 200:
                                    installations = await response.json()
                                    return installations
                                
                    async def get_repositories(installation):
                        repositories_url = f'https://api.github.com/installation/repositories'
                        token = await GithubAPI().authenticate_app_as_installation(installation["account"]["login"])
                        headers = {
                        'Authorization': f'Bearer {token}',
                        'Accept': 'application/vnd.github.machine-man-preview+json'  # Required for accessing GitHub app APIs
                    }

                        async with aiohttp.ClientSession(headers=headers) as session:
                            async with session.get(repositories_url) as response:
                                # print(await response.json(), file=sys.stderr)
                                if response.status == 200:
                                    data = await response.json()
                                    
                                    return data["repositories"]
                    

                    async def get_comments(repository):
                        # print(repository, file=sys.stderr)
                        repository_owner = repository['owner']['login']
                        repository_name = repository['name']
                        comments_url = f'https://api.github.com/repos/{repository_owner}/{repository_name}/comments'

                        headers = {
                        'Authorization': f'Bearer {os.getenv("GithubPAT")}',
                        'Accept': 'application/vnd.github.machine-man-preview+json'  # Required for accessing GitHub app APIs
                    }
                        

                        async with aiohttp.ClientSession(headers=headers) as session:
                            async with session.get(comments_url) as response:
                                if response.status == 200:
                                    comments = await response.json()
                                    # print(comments, file=sys.stderr)
                                    return comments
                    
                    comments = []
                    
                    app_installations = await get_installations()
                    for installation in app_installations:
                        repositories = await get_repositories(installation)
                        if repositories:
                            print("----RePO-----", file=sys.stderr)
                            for repo in repositories:
                                print(installation["account"]["login"]+'/'+repo["name"], file=sys.stderr)
                                # print(repo, file=sys.stderr)
                                # data = await get_comments(repo)
                                # if data:
                                #     comments+=data
                    
                    count = 0
                    for comment in comments:
                        # print(comment)
                        if comment["user"]["login"] == "c4gt-community-support[bot]":
                            count+=1
                    print(count, file=sys.stderr)
                    return app_installations
                    

                    
                        # repo = issue["repository_url"].split('/')[-1]
                        # owner = issue["repository_url"].split('/')[-2]
                        # token  = GithubAPI().authenticate_app_as_installation(repo_owner=owner)
                        # print(token, file=sys.stderr)
                        # head = {
                        #     'Accept': 'application/vnd.github+json',
                        #     'Authorization': f'Bearer {token}'
                        # }
                        # body = "The following headers are missing or misspelled in the metadata:"
                        # for header in missing_headers:
                        #     body+= f'\n{header}'
                        # url = f'https://api.github.com/repos/{owner}/{repo}/issues/{data["issue"]["number"]}/comments'
                        # print(5,file=sys.stderr)
                        # print(requests.post(url, json={"body":body}, headers=head).json(), file=sys.stderr)
                        # return data
    


    
