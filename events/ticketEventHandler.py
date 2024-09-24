# Tickets are created, edited and deleted
# Comments are created edited and deleted

import aiohttp
import os, sys, datetime, json
from utils.db import PostgresORM
from utils.markdown_handler import MarkdownHeaders
from utils.github_api import GithubAPI
from utils.jwt_generator import GenerateJWT
from aiographql.client import GraphQLClient, GraphQLRequest
from events.ticketFeedbackHandler import TicketFeedbackHandler
# from githubdatapipeline.issues.processor import closing_pr
import postgrest
from githubdatapipeline.issues.processor import returnConnectedPRs
from fuzzywuzzy import fuzz
import logging
from urllib.parse import urlparse
import re
from datetime import datetime

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
    discord_channels = await PostgresORM().readAll("discord_channels")
    products = await PostgresORM().readAll("product")

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
        self.postgres_client = PostgresORM()
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
        try:
            issue = eventData["issue"]

            is_issue = await self.postgres_client.get_issue_from_issue_id(issue["id"])
            if is_issue:
                return await self.onTicketEdit(eventData)
            print(f'ticket creation called at {datetime.now()} with {issue}')
            if any(label["name"].lower() in ["c4gt community".lower(), "dmp 2024"] for label in issue["labels"] ):
                if any(label["name"].lower() == "c4gt community" for label in issue["labels"]):
                    ticketType = "ccbp"
                else:
                    ticketType = "dmp"
                markdown_contents = MarkdownHeaders().flattenAndParse(issue["body"])
                # print(markdown_contents, file=sys.stderr)
                parsed_url = urlparse(issue["url"])
                path_segments = parsed_url.path.split('/')
                repository_owner = path_segments[2]
                org = await self.postgres_client.get_data("name", "community_orgs", repository_owner)
                if org is None:
                    org = await self.postgres_client.add_data(data={"name":repository_owner}, table_name="community_orgs")
                complexity = markdown_contents.get("Complexity")
                advisor = markdown_contents.get("Advisor")
                mentor = markdown_contents.get("Mentors")
                contributor = markdown_contents.get("Contributor")
                designer = markdown_contents.get("Designer")
                labels = issue["labels"]
                print("complexity", complexity)
                ticket_data = {
                        "title":issue["title"],     #name of ticket
                        "description":  markdown_contents,
                        "complexity": markdown_contents["Complexity"].lower() if markdown_contents.get("Complexity") else None ,
                        "technology": markdown_contents["Tech Skills Needed"].lower() if markdown_contents.get("Tech Skills Needed") else None, 
                        "status": issue["state"],
                        "link": issue["html_url"],
                        "org_id": org[0]["id"],
                        "labels": [l['name'] for l in labels],
                        "issue_id": issue["id"],
                        "created_at": issue["created_at"] if issue.get("created_at") else None,
                }
                if ticketType == "ccbp":
                    recorded_data = await self.postgres_client.record_created_ticket(data=ticket_data,table_name="issues")
                    print("recorded issue data ", recorded_data)
                    added_contributor = await self.add_contributor(issue)
                    if added_contributor:
                        print('contributors data added')
                    else:
                        print('could not add contributors data')
                    #add mentor's here

                

                else:
                    print("TICKET NOT ADDED", ticket_data, file=sys.stderr)
                    await self.postgres_client.add_data("issues", ticket_data)

                if TicketFeedbackHandler().evaluateDict(markdown_contents) and ticketType == "ccbp":
                    url_components = issue["url"].split('/')
                    issue_number = url_components[-1]
                    repo = url_components[-3]
                    owner = url_components[-4]
                    try:                    
                        await PostgresORM().add_data({"issue_id":issue["id"],"updated_at": datetime.utcnow().isoformat()},"app_comments")
                        comment = await TicketFeedbackHandler().createComment(owner, repo, issue_number, markdown_contents)
                        if comment:
                                
                            await PostgresORM().update_data({
                                "api_url":comment["url"],
                                "comment_id":comment["id"],
                                "issue_id":issue["id"],
                                "updated_at": datetime.utcnow().isoformat()
                            },"issue_id","app_comments")
                            
                    except Exception as e:
                        print("Issue already commented ", e)
            return eventData
        except Exception as e:
            print('exception occured while creating ticket ', e)
            
        

    async def onTicketEdit(self, eventData):
        issue = eventData["issue"]
        print(f'edit ticket called at {datetime.now()} with {issue}')
    
        if any(label["name"].lower() == "c4gt community" for label in issue["labels"]):
            ticketType = "ccbp"
        markdown_contents = MarkdownHeaders().flattenAndParse(issue["body"])
        print("MARKDOWN", markdown_contents, file=sys.stderr )
        parsed_url = urlparse(issue["url"])
        path_segments = parsed_url.path.split('/')
        repository_owner = path_segments[2]
        org = await self.postgres_client.get_data("name", "community_orgs", repository_owner)
        if org is None:
            org = await self.postgres_client.insert_org(repository_owner)
        complexity = markdown_contents.get("Complexity")
        advisor = markdown_contents.get("Advisor")
        mentor = markdown_contents.get("Mentors")
        contributor = markdown_contents.get("Contributor")
        designer = markdown_contents.get("Designer")
        labels = issue["labels"]
        print("complexity", complexity)
        ticket_data = {
                "title":issue["title"],     #name of ticket
                "description":  markdown_contents,
                "complexity": markdown_contents["Complexity"].lower() if markdown_contents.get("Complexity") else None ,
                "technology": markdown_contents["Tech Skills Needed"].lower() if markdown_contents.get("Tech Skills Needed") else None, 
                "status": issue["state"],
                "link": issue["html_url"],
                "org_id": org[0]["id"],
                "labels": [l['name'] for l in labels],
                "issue_id": issue["id"],
                "created_at": issue["created_at"] if issue.get("created_at") else None,
        }
        # print("TICKET", ticket_data, file=sys.stderr)
        if ticketType == "ccbp":
            await self.postgres_client.update_data(ticket_data,"issue_id","issues")

        if await PostgresORM().check_record_exists("app_comments","issue_id",issue["id"]) and ticketType=="ccbp":
            url_components = issue["url"].split('/')
            repo = url_components[-3]
            owner = url_components[-4]
            comment_id = await PostgresORM().get_data("issue_id","app_comments",issue["id"],None)[0]["comment_id"]
            if TicketFeedbackHandler().evaluateDict(markdown_contents):
                comment = await TicketFeedbackHandler().updateComment(owner, repo, comment_id, markdown_contents)
                if comment:
                    
                    await PostgresORM.get_instance().update_data({
                        "updated_at": datetime.utcnow().isoformat(),
                        "issue_id": issue["id"]
                    },"issue_id","app_comments")
            else:
                try:
                    comment = await TicketFeedbackHandler().deleteComment(owner, repo, comment_id)
                    print(f"Print Delete Task,{comment}", file=sys.stderr)
                    print(await PostgresORM.get_instance().deleteComment(issue["id"],"app_comments"))
                except:
                    print("Error in deletion")
        elif ticketType=="ccbp":
            if TicketFeedbackHandler().evaluateDict(markdown_contents):
                url_components = issue["url"].split('/')
                issue_number = url_components[-1]
                repo = url_components[-3]
                owner = url_components[-4]
                try:
                    
                    
                    await PostgresORM().add_data({
                            "issue_id":issue["id"],
                            "updated_at": datetime.utcnow().isoformat()
                        },"app_comments")
                    comment = await TicketFeedbackHandler().createComment(owner, repo, issue_number, markdown_contents)
                    if comment:
                                                
                        await PostgresORM().update_data({
                            "api_url":comment["url"],
                            "comment_id":comment["id"],
                            "issue_id":issue["id"],
                            "updated_at": datetime.utcnow().isoformat()
                        },"issue_id","app_comments")
                        
                except Exception as e:
                    print("Issue already commented ", e)

        return eventData
    
    async def onTicketClose(self, eventData):
        issue_update = {
            "status":"closed",
            "issue_id": eventData["id"]
        }
        issue_details = await self.postgres_client.update_data(issue_update, "issue_id", "issues")


        issue = await self.postgres_client.get_issue_from_issue_id(eventData['id'])                
        contributors = await self.postgres_client.get_contributors_from_issue_id(issue[0]['id']) if issue else None
        
        #FIND POINTS BY ISSUE COMPLEXITY
        points = await self.postgres_client.get_pointsby_complexity(issue[0]['complexity'])
        
        #SAVE POINT IN POINT_TRANSACTIONS & USER POINTS
        add_points = await self.postgres_client.upsert_point_transaction(issue[0]['id'],contributors[0]['contributor_id'],points)
        add_user_points= await self.postgres_client.save_user_points(contributors[0]['contributor_id'],points)
                    

        #allot points
        issue_details = await self.postgres_client.get_data("url","issues", eventData['issue_url'],None)
        
        # complexity = issue_details["complexity"]
        # points = await self.postgres_client.get_data("complexity","point_system", complexity,None)

        # assignee = eventData["assignees"][0]["id"]

        # user_id = await self.postgres_client.get_data("github_id","contributors_registration", assignee,None)
        # mentor_id = await self.postgres_client.get_data("issue_id", "issue_mentors", issue_details["id"], None)
        # point_transaction = {
        #     "user_id": user_id["id"],
        #     "issue_id": issue_details["id"],
        #     "point": points["points"],
        #     "type": "credit",
        #     "mentor_id": mentor_id,
        #     "created_at": datetime.now(),
        #     "updated_at": datetime.now()
        # }  
        
        # print('points_transaction is ', point_transaction)

        # inserted_data = await self.postgres_client.add_data(point_transaction, "point_transactions")
                    
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

    def extract_section(self, content, section_title):
        pattern = rf"<.*?> {section_title}\s*(.*?)\s<.*?>"
       
        match = re.findall(pattern, content)
        if match:
            return match.group(1).strip()
        return None
          
    async def processDescription(self, eventData):
        action = eventData["action"]
        issue = eventData["issue"]
       
        print('processing description ', issue)
        markdown_contents = MarkdownHeaders().flattenAndParse(issue["body"])
        print(markdown_contents)
    # print(markdown_contents, file=sys.stderr)
        parsed_url = urlparse(issue["url"])
        path_segments = parsed_url.path.split('/')
        repository_owner = path_segments[2]
        org = await self.postgres_client.get_data("name", "community_orgs", repository_owner)
        complexity = markdown_contents.get("Complexity")
        print("complexity", complexity)
        ticket_data = {
                    "title":issue["title"],     #name of ticket
                    "description":  markdown_contents,
                    "complexity": markdown_contents["Complexity"].lower() if markdown_contents.get("Complexity") else None ,
                    "technology": markdown_contents["Tech Skills Needed"].lower() if markdown_contents.get("Tech Skills Needed") else None, 
                    "status": issue["state"],
                    "link": issue["html_url"],
                    "org_id": org[0]["id"],
                    "labels":issue["labels"],
                    "issue_id": issue["id"],
                    "advisor": markdown_contents["Advisor"] if markdown_contents["Advisor"] else None,
                    "mentor": markdown_contents["Mentor"] if markdown_contents["Mentor"] else None, 
                    "contributor": markdown_contents["Contributor"] if markdown_contents["Contributor"] else None,
                    "designer": markdown_contents["Designer"] if markdown_contents["Designer"] else None,
                    "created_at": issue["created_at"] if issue.get("created_at") else None,
                    "updated_at": issue["updated_at"] if issue.get("updated_at") else None,
                }
        print("ticket_data", ticket_data)
        self.postgres_client.add_data(ticket_data, "issues")
        return ticket_data


    async def add_contributor(self, issue):
        try:
            markdown_contents = MarkdownHeaders().flattenAndParse(issue["body"])
            assignee = issue["assignee"]
            get_issue = await self.postgres_client.get_data("issue_id", "issues", issue["id"])
            if assignee:
                contributors_id = assignee["id"]
            else:
                contributors_id = markdown_contents.get("Contributor")
            user = await self.postgres_client.get_data("github_id","contributors_registration", contributors_id, None)
            contributors_data = {
                            "issue_id": get_issue[0]["id"],
                            "role": 1,
                            "contributor_id": user[0]["id"] if user else None,
                            "created_at":str(datetime.now()),
                            "updated_at":str(datetime.now())
                        }
            inserted_data = await self.postgres_client.add_data(contributors_data, "issue_contributors")
            return inserted_data
        except Exception as e:
            print('exception while adding contributors data ',e)
            return None

        


    


    
