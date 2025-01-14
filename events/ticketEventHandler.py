# Tickets are created, edited and deleted
# Comments are created edited and deleted

import aiohttp
import os, sys, datetime, json
from shared_migrations.db.server import ServerQueries
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
import json
from datetime import datetime
import markdown

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
    discord_channels = await ServerQueries().readAll("discord_channels")
    products = await ServerQueries().readAll("product")

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
        self.postgres_client = ServerQueries()
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
    
    def convert_to_datetime(self, date_str):
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
    
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
                # parsed_url = urlparse(issue["url"])
                # path_segments = parsed_url.path.split('/')
                # repository_owner = path_segments[2]
                organization = markdown_contents.get("Organisation Name")
                # org_array = []
                org = await self.postgres_client.get_data("name", "community_orgs", organization)
                if org is None:
                    new_org = await self.postgres_client.add_data(data={"name":organization}, table_name="community_orgs")
                    org = await self.postgres_client.get_data("name", "community_orgs", organization)
                
                
                complexity = markdown_contents.get("Complexity")
                advisor = markdown_contents.get("Advisor")
                mentor = markdown_contents.get("Mentor(s)")
                contributor = markdown_contents.get("Contributor")
                designer = markdown_contents.get("Designer")

                labels = issue["labels"]  # Assuming this contains the list of labels
                desired_labels = ['C4GT Coding', 'C4GT Advisory', 'C4GT Mentorship', 'C4GT Design', 'C4GT Bounty', 'C4GT Community']
                # Filter the labels to include only the desired ones
                filtered_labels = []
                for label in labels:
                    if label["name"] in desired_labels:
                        filtered_labels.append(label["name"])

                print('filtered labels ', filtered_labels)

                category = markdown_contents.get("Category")
                domain = markdown_contents.get("Domain")
                print("complexity", complexity)
                created_at =  issue["created_at"] if issue.get("created_at") else None
                if created_at:
                    created_at = self.convert_to_datetime(created_at)

                updated_at = issue["updated_at"] if issue.get("updated_at") else None
                if updated_at:
                    updated_at = self.convert_to_datetime(updated_at)
                ticket_data = {
                        "title":issue["title"],     #name of ticket
                        "description":  markdown_contents,
                        "complexity": markdown_contents["Complexity"] if markdown_contents.get("Complexity") else None ,
                        "technology": markdown_contents["Tech Skills Needed"] if markdown_contents.get("Tech Skills Needed") else None, 
                        "status": issue["state"],
                        "link": issue["html_url"],
                        "org_id": org[0]["id"],
                        "labels": filtered_labels,
                        "issue_id": issue["id"],
                        "created_at": created_at,
                        "domain": domain,
                        "project_type": category,
                        "updated_at": updated_at
                }
                print('ticket_data is ', ticket_data)
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
                        await self.postgres_client.add_data({"issue_id":issue["id"],"updated_at": datetime.utcnow().isoformat()},"app_comments")
                        comment = await TicketFeedbackHandler().createComment(owner, repo, issue_number, markdown_contents)
                        if comment:
                                
                            await self.postgres_client.update_data({
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
        else:
            ticketType = "dmp"
        
        print(f'calling markdown parser with {issue["body"]}')
        markdown_contents = MarkdownHeaders().flattenAndParse(issue["body"])
        print("MARKDOWN", markdown_contents, file=sys.stderr )
        # parsed_url = urlparse(issue["url"])
        # path_segments = parsed_url.path.split('/')
        # repository_owner = path_segments[2]
        organization = markdown_contents.get("Organisation Name")
        # org_array = []
        org = await self.postgres_client.get_data("name", "community_orgs", organization)
        if org is None:
            new_org = await self.postgres_client.add_data(data={"name":organization}, table_name="community_orgs")
            org = await self.postgres_client.get_data("name", "community_orgs", organization)
        complexity = markdown_contents.get("Complexity")
        advisor = markdown_contents.get("Advisor")
        mentor = markdown_contents.get("Mentors")
        contributor = markdown_contents.get("Contributor")
        designer = markdown_contents.get("Designer")

        labels = issue["labels"]  # Assuming this contains the list of labels
        desired_labels = ['C4GT Coding', 'C4GT Advisory', 'C4GT Mentorship', 'C4GT Design', 'C4GT Bounty', 'C4GT Community']
        # Filter the labels to include only the desired ones
        filtered_labels = []
        for label in labels:
            if label["name"] in desired_labels:
                filtered_labels.append(label["name"])

        print('filtered labels ', filtered_labels)

        category = markdown_contents.get("Category")
        domain = markdown_contents.get("Domain")
        print("complexity", complexity)
        created_at =  issue["created_at"] if issue.get("created_at") else None
        if created_at:
            created_at = self.convert_to_datetime(created_at)

        updated_at = issue["updated_at"] if issue.get("updated_at") else None
        if updated_at:
            updated_at = self.convert_to_datetime(updated_at)
        ticket_data = {
                "title":issue["title"],     #name of ticket
                "description":  markdown_contents,
                "complexity": markdown_contents["Complexity"] if markdown_contents.get("Complexity") else None ,
                "technology": markdown_contents["Tech Skills Needed"] if markdown_contents.get("Tech Skills Needed") else None, 
                "status": issue["state"],
                "link": issue["html_url"],
                "org_id": org[0]["id"],
                "labels": filtered_labels,
                "issue_id": issue["id"],
                "project_type": category,
                "domain": domain,
                "created_at": created_at,
                "updated_at": updated_at
        }
        # print("TICKET", ticket_data, file=sys.stderr)
        if ticketType == "ccbp":
            await self.postgres_client.record_updated_ticket(ticket_data, "issues")
            added_contributor = await self.add_contributor(issue)
            if added_contributor:
                print('contributors data added')

        if await self.postgres_client.check_record_exists("app_comments","issue_id",issue["id"]) and ticketType=="ccbp":
            url_components = issue["url"].split('/')
            repo = url_components[-3]
            owner = url_components[-4]
            comments = await self.postgres_client.get_data("issue_id","app_comments",issue["id"],None)
            comment_id = comments[0]["comment_id"]
            if TicketFeedbackHandler().evaluateDict(markdown_contents):
                comment = await TicketFeedbackHandler().updateComment(owner, repo, comment_id, markdown_contents)
                if comment:
                    
                    await self.postgres_client.update_data({
                        "updated_at": datetime.utcnow().isoformat(),
                        "issue_id": issue["id"]
                    },"issue_id","app_comments")
            else:
                try:
                    comment = await TicketFeedbackHandler().deleteComment(owner, repo, comment_id)
                    print(f"Print Delete Task,{comment}", file=sys.stderr)
                    print(await self.postgres_client.deleteComment(issue["id"],"app_comments"))
                except:
                    print("Error in deletion")
        elif ticketType=="ccbp":
            if TicketFeedbackHandler().evaluateDict(markdown_contents):
                url_components = issue["url"].split('/')
                issue_number = url_components[-1]
                repo = url_components[-3]
                owner = url_components[-4]
                try:
                    
                    
                    await self.postgres_client.add_data({
                            "issue_id":issue["id"],
                            "updated_at": datetime.utcnow().isoformat()
                        },"app_comments")
                    comment = await TicketFeedbackHandler().createComment(owner, repo, issue_number, markdown_contents)
                    if comment:
                                                
                        await self.postgres_client.update_data({
                            "api_url":comment["url"],
                            "comment_id":comment["id"],
                            "issue_id":issue["id"],
                            "updated_at": datetime.utcnow().isoformat()
                        },"issue_id","app_comments")
                        
                except Exception as e:
                    print("Issue already commented ", e)

        return eventData
    
    async def onTicketClose(self, eventData):
        try:
            issue_update = {
                "status":"closed",
                "issue_id": eventData["id"]
            }

            print('issue_update in ticket close is ', issue_update)
            issue_details = await self.postgres_client.update_data(issue_update, "issue_id", "issues")
            print('issue details ', issue_details)

            issue = await self.postgres_client.get_issue_from_issue_id(eventData['id'])   
            print('issue is ', issue)             
            contributors = await self.postgres_client.get_contributors_from_issue_id(issue[0]['id']) if issue else None
            print('contributor is', contributors )
            #FIND POINTS BY ISSUE COMPLEXITY
            points = await self.postgres_client.get_pointsby_complexity(issue[0]['complexity'].lower())
            print('points is ', points)
            user_id = await self.postgres_client.get_data("id","contributors_registration", contributors[0]['contributor_id'],None)
            print('user is ', user_id)

            markdown_contents = MarkdownHeaders().flattenAndParse(eventData["body"])
            angel_mentor = markdown_contents.get("Angel Mentor")
            angel_mentor_detials = []
            if angel_mentor:
                url = f'https://api.github.com/users/{angel_mentor}'
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        angel_mentor_data = await response.json()
                if angel_mentor_data:
                    angel_mentor_id = angel_mentor_data["id"]
                    angel_mentor_detials = await self.postgres_client.get_data("github_id","contributors_registration", angel_mentor_id)
            print('mentor is ', angel_mentor_detials)
            point_transaction = {
                "user_id": user_id[0]['id'],
                "issue_id": issue[0]["id"],
                "point": points,
                "type": "credit",
                "angel_mentor_id": angel_mentor_detials[0]['id'] if angel_mentor_detials else None,
                "created_at": str(datetime.now()),
                "updated_at": str(datetime.now())
            }  
            
            print('points_transaction is ', point_transaction)
            print('inserting data in point_transactions')
            inserted_data = await self.postgres_client.add_data(point_transaction, "point_transactions")
                        
            return
        except Exception as e:
            print(f"An error occurred - ticket close: {e}")
            return 'failed'
        
    
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
 
    async def get_mentors_urls(self, body):
        cleaned_body = body.replace('\\r\\n', '\n')

        # Updated regex to capture the 'Mentor(s)' section, allowing for newlines and text after it
        mentors_match = re.search(r"## Mentor\(s\)\s*\n\s*\n(.+?)(\n##|$)", cleaned_body, re.DOTALL)

        if mentors_match:
            mentors_details = mentors_match.group(1).strip()
            # Extract the URL part only using another regex
            url_match = re.search(r"\[.*?\]\((https://github\.com/.*?)\)", mentors_details)
            if url_match:
                mentor_url = url_match.group(1)
                print("Mentor(s) URL:", mentor_url)
                return mentor_url
            else:
                print("Mentor(s) URL not found.")
        else:
            print("Mentor(s) section not found.")
        
        return None

    
    async def add_contributor(self, issue):
        try:
            markdown_contents = MarkdownHeaders().flattenAndParse(issue["body"])
            assignee = issue["assignee"]
            get_issue = await self.postgres_client.get_data("issue_id", "issues", issue["id"])
            if assignee:
                contributors_id = assignee["id"]
            else:
                contributors_id = markdown_contents.get("Contributor")
            user = await self.postgres_client.get_data("github_id","contributors_registration", contributors_id)
            contributors_data = {
                            "issue_id": get_issue[0]["id"],
                            "role": 1,
                            "contributor_id": user[0]["id"] if user else None,
                            "created_at":str(datetime.now()),
                            "updated_at":str(datetime.now())
                        }
            inserted_data = await self.postgres_client.add_data(contributors_data, "issue_contributors")

            #add mentor's data
            org_mentor = markdown_contents.get("Organizational Mentor")
            angel_mentor = markdown_contents.get("Angel Mentor")
            if angel_mentor:
                pass
            else:
                angel_mentor = markdown_contents.get("Mentor(s)")
          
            angel_mentor_detials = []
            if angel_mentor: 
                url = f'https://api.github.com/users/{angel_mentor}'
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        angel_mentor_data = await response.json()
                if angel_mentor_data:
                    angel_mentor_id = angel_mentor_data["id"]
                    angel_mentor_detials = await self.postgres_client.get_data("github_id","contributors_registration", angel_mentor_id)          
            mentor_data = {
                "issue_id": get_issue[0]["id"],
                "org_mentor_id": org_mentor if org_mentor else None,
                "angel_mentor_id":angel_mentor_detials[0]['id'] if angel_mentor_detials else None,
                "created_at":str(datetime.now()),
                "updated_at":str(datetime.now())
            }
            inserted_mentor = await self.postgres_client.add_data(mentor_data, "issue_mentors")
            if not inserted_mentor:
                print('mentor data could not be inserted')
        
            return inserted_data
        except Exception as e:
            print('exception while adding contributors data ',e)
            return None

        
    async def add_assignee(self, issue):
        try:
            issue_exist = await self.postgres_client.get_data('issue_id', 'issues', issue["id"])
            if issue_exist:
                assignee = issue["assignee"]
                if assignee:
                    contributors_id = assignee["id"]
                    user = await self.postgres_client.get_data("github_id","contributors_registration", contributors_id)
                    contributors_data = {
                                    "issue_id": issue_exist[0]["id"],
                                    "role": 1,
                                    "contributor_id": user[0]["id"] if user else None,
                                    "created_at":str(datetime.now()),
                                    "updated_at":str(datetime.now())
                                }
                    inserted_data = await self.postgres_client.add_data(contributors_data, "issue_contributors")
                    if inserted_data:
                        print('assignee added ', inserted_data)
                        return inserted_data
            
            print('could not add assignee')
            return 'success'

        except Exception as e:
            print('exception occured while assigning an assignee to a ticket ', e)
            raise Exception
        
    


    
