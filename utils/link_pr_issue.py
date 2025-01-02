import aiohttp
import os, re, httpx, time
from datetime import datetime
from shared_migrations.db.server import ServerQueries

class AddIssueId:
    def __init__(self):
        self.postgres_client = ServerQueries()
        return
    
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
            headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            
            GITHUB_ISSUE_URL = "https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
            
            description_url = GITHUB_ISSUE_URL.format(
                owner=owner, repo=repo, issue_number=issue_number)
            async with httpx.AsyncClient() as client:
                issue_response = await client.get(description_url, headers=headers)
                if issue_response.status_code == 200:
                    
                    issue_details = issue_response.json()
                    issue_id = issue_details["id"]
                    return issue_id
                
            return None
        except Exception as e:
            print('Exception occured while getting issue data ', e)
            return None
    
    async def process_prs(self):
        try:
            all_prs = await self.postgres_client.readAll('pr_history')
            print('length of all prs is ', len(all_prs))

            GITHUB_TOKEN = os.getenv('API_TOKEN')
            headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "X-GitHub-Api-Version": "2022-11-28"
            }

            for pr in all_prs:
                time.sleep(2)
                print('processing pr id #', pr["id"])
                api_url = pr["api_url"]
                
                pr_data = None
                async with aiohttp.ClientSession() as session:
                    async with session.get(api_url, headers=headers) as response:
                        if response.status == 200:
                            pr_data = await response.json()
                if pr_data:
                    pr_title = pr_data["title"]
                    issue_number = self.extract_issue_number(pr_title)
                    if issue_number:
                        url_parts = api_url.split('/')
                        owner = url_parts[4]
                        repo = url_parts[5]
                        issue_id = await self.get_issue_data(owner, repo, issue_number)
                        
                        if issue_id:
                            pr["issue_id"] = issue_id
                            pr["title"] = pr_title
                            pr["created_at"] = pr["created_at"].replace(tzinfo=None)
                            pr["raised_at"] = pr["raised_at"].replace(tzinfo=None)
                            await self.postgres_client.update_data(pr, 'id', 'pr_history')

            return 'updated'

        except Exception as e:
            print('exception occured while processing PRs ', e)
            return 'failed'