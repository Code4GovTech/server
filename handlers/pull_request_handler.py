import logging, httpx, os, re, aiohttp

from sqlalchemy.util import ellipses_string

from handlers.EventHandler import EventHandler
from datetime import datetime
from utils.user_activity import UserActivity
from shared_migrations.db.server import ServerQueries

class Pull_requestHandler(EventHandler):

    def convert_to_datetime(self, date_str):
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
    
    def extract_issue_number(self, title):
        match = re.search(r'#(\d+)', title)
        if match:
            return int(match.group(1))  
        return None
    
    async def get_issue_data(self, owner, repo, issue_number):
        try:
            GITHUB_TOKEN = os.getenv('API_TOKEN')
            print('github token is ', GITHUB_TOKEN)
            headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            
            GITHUB_ISSUE_URL = "https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
            print('inside get issue id for issue number ',issue_number )
            description_url = GITHUB_ISSUE_URL.format(
                owner=owner, repo=repo, issue_number=issue_number)
            async with httpx.AsyncClient() as client:
                issue_response = await client.get(description_url, headers=headers)
                print('issue response inside get issue id for pr is ', issue_response)
                if issue_response.status_code == 200:
                    
                    issue_details = issue_response.json()
                    print('issue_details after fetching is ', issue_details)
                    issue_id = issue_details["id"]
                    print('issue id after fetching ', issue_id)
                    return issue_id
                
            return None
        except Exception as e:
            print('Exception occured while getting issue data ', e)
            return None
    

    async def handle_event(self, data, dummy_ps_client):
        # Implement your logic for handling issue events here
        try:
            print('inside pull request handler ', data) 

            postgres_client = ServerQueries()

            # merged_by =  data['pull_request']['merged_by']['id'] if data['pull_request']['merged_by'] else None
            merged_by = data.get("pull_request", {}).get("merged_by", {}).get('id', None)
            merged_at = data['pull_request']['merged_at']
            # merged_by_username =  data['pull_request']['merged_by']['login'] if data['pull_request']['merged_by'] else None
            merged_by_username = data.get("pull_request", {}).get("merged_by", {}).get('login', None)
            created_at =  self.convert_to_datetime(data['pull_request']['created_at'])
            raised_at = self.convert_to_datetime(data['pull_request']['updated_at'])
            if merged_at:
                merged_at = self.convert_to_datetime(merged_at)

            api_url = data['pull_request']["url"]
                
            issue_id = None


            # async with aiohttp.ClientSession() as session:
            #     async with session.get(api_url) as response:
            #         pr_data = await response.json()
            # if pr_data:
            #     pr_title = pr_data["title"]
            #     issue_number = self.extract_issue_number(pr_title)
            #     if issue_number:
            #         url_parts = api_url.split('/')
            #         owner = url_parts[4]
            #         repo = url_parts[5]
            #         issue_id = await self.get_issue_data(owner, repo, issue_number)

            try:
                pr_title = data.get("pull_request", {}).get("title", None)
                if pr_title is not None:
                    issue_number = self.extract_issue_number(pr_title)
                    if issue_number:
                        url_parts = api_url.split('/')
                        owner = url_parts[4]
                        repo = url_parts[5]

                        issue_link = f"https://github.com/{owner}/{repo}/issues/{issue_number}"
                        issue_data = await postgres_client.get_data('link', 'issues',  issue_link)
                        if issue_data:
                            issue_id = issue_data[0].get("issue_id", None) if issue_data[0] else None
            except Exception as e:
                print("Error getting issue from PR title - ", e)


            
            pr_data = {
                "created_at": created_at,
                "api_url":data['pull_request']['url'],
                "html_url": data['pull_request']['html_url'],
                "raised_by": data['pull_request']['user']['id'],
                "raised_at":  raised_at,
                "raised_by_username": data['pull_request']['user']['login'],
                "status": data['action'],
                # "is_merged": data['pull_request']['merged'],
                "is_merged": data.get("pull_request", {}).get("merged", False),
                "merged_by": merged_by,
                "merged_at": str(merged_at),
                "merged_by_username":  merged_by_username,
                "pr_id": data['pull_request']['id'],
                "ticket_url": data['pull_request']['issue_url'],
                "title": data['pull_request']['title'],
                # "issue_id": issue_id if issue_id else None,
                "issue_id": issue_id,
                "ticket_complexity": None
            }

            print('PR data ', pr_data)
            
            pr_exist = await postgres_client.get_data('pr_id', 'pr_history',  data['pull_request']['id'])
            if pr_exist:
                save_data = await postgres_client.update_pr_history(pr_data["pr_id"],pr_data)
            else:
                save_data = await postgres_client.add_data(pr_data,"pr_history")
            print('saved data in PR ', save_data)            
            if save_data == None:
                logging.info("Failed to save data in pr_history")

            user_id = data['pull_request']['user']['id']

            #get contributor_id and save to supabase
            contributor = await postgres_client.get_data('github_id', 'contributors_registration', user_id)
            if not contributor:
                print('could not add contributors data contributor does not exist')
                return pr_data
            contributor_id = contributor[0]["id"]

            issue_url = data['pull_request']['issue_url']
            issue = await postgres_client.get_data('link', 'issues', issue_url, '*')

            #save activity to user_activity
            await UserActivity.log_user_activity(data, 'pull_request')
        except Exception as e:
            print('exception in pr ', e)
            logging.info(e)
            raise Exception
        
        

