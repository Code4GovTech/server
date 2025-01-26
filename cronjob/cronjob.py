import asyncio
from datetime import datetime, timezone, timedelta
import httpx
import jwt
# from jwt import JWT
import os
from dotenv import load_dotenv
import logging
import sys
import time

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from utils.jwt_generator import GenerateJWT
from utils.new_jwt_generator import NewGenerateJWT

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# from ..handlers.issues_handler import IssuesHandler
# from handlers.pull_request_handler import Pull_requestHandler

from handlers.issues_handler import IssuesHandler
from handlers.pull_request_handler import Pull_requestHandler
from handlers.issue_comment_handler import Issue_commentHandler

from shared_migrations.db.server import ServerQueries, get_postgres_uri


load_dotenv()

class CronJob():

    def __init__(self):
        self.postgres_client = ServerQueries()
        # self.jwt_generator = GenerateJWT()
        self.jwt_generator = NewGenerateJWT()

    def get_github_jwt(self):
        pem = os.getenv('pem_file')
        client_id = os.getenv('client_id')

        try:
            with open(pem, 'rb') as pem_file:
                signing_key = pem_file.read()
                payload = {
                    'iat': datetime.now(timezone.utc),
                    'exp': datetime.now(timezone.utc) + timedelta(seconds=600),
                    'iss': client_id
                }
                encoded_jwt = jwt.encode(payload, signing_key, algorithm='RS256')
                pem_file.close()
            return encoded_jwt
        except Exception as e:
            logging.error(f"In get_github_jwt: {e}")
            return None


    async def get_rate_limits(self, token_headers: dict):
        rate_limit_url = "https://api.github.com/rate_limit"
        async with httpx.AsyncClient() as client:
            rate_limit_resp = await client.get(rate_limit_url, headers=token_headers)
            return rate_limit_resp.json()


    async def get_installations(self, token_headers: dict):
        async with httpx.AsyncClient() as client:
            get_installations_url = 'https://api.github.com/app/installations'
            installations_response = await client.get(get_installations_url, headers=token_headers)
            if installations_response.status_code == 200:
                return installations_response.json()
            elif installations_response.status_code == 401:
                if installations_response.json().get("message",
                                                    None) == '\'Expiration time\' claim (\'exp\') must be a numeric value representing the future time at which the assertion expires':
                    logging.info("JWT expired at get_installation stage")
                    return -1


    async def get_access_token(self, token_headers: dict, installation_id: str):
        async with httpx.AsyncClient() as client:
            access_token_url = f"https://api.github.com/" \
                            f"app/installations/{installation_id}/access_tokens"
            access_token_response = await client.post(url=access_token_url,
                                                    headers=token_headers)

            await asyncio.sleep(0.5)

            if access_token_response.status_code == 201:
                return access_token_response.json().get('token', None)
            elif access_token_response.status_code == 401:
                if access_token_response.json().get("message",
                                                    None) == '\'Expiration time\' claim (\'exp\') must be a numeric value representing the future time at which the assertion expires':
                    logging.info("JWT expired at get_access_token stage")
                    return -1
            else:
                return None


    async def get_repos(self, token: str):
        async with httpx.AsyncClient() as client:
            token_headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            list_repo_url = "https://api.github.com/installation/repositories"
            repo_response = await client.get(url=list_repo_url,
                                            headers=token_headers)
            if repo_response.status_code == 200:
                repo_data = repo_response.json()
                return repo_data.get('repositories', [])


    async def get_issues(self, token: str, repo_fullname):
        get_issue_url = f"https://api.github.com/repos/{repo_fullname}/issues"
        token_headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        payload = {"labels": "c4gt community"}
        async with httpx.AsyncClient() as client:
            issues_response = await client.get(url=get_issue_url,
                                            headers=token_headers,
                                            params=payload
                                            )
            return issues_response.json()

    async def get_issue_comments(self, issue_comment_url):
       
        async with httpx.AsyncClient() as client:
            issue_comment_response = await client.get(url=issue_comment_url)
            return issue_comment_response.json()

    async def get_pull_requests(self, token: str, repo_fullname):
        get_pull_requests_url = f"https://api.github.com/repos/{repo_fullname}/pulls"
        token_headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        async with httpx.AsyncClient() as client:
            pull_requests_response = await client.get(url=get_pull_requests_url,
                                                    headers=token_headers
                                                    )
            pull_requests_data = pull_requests_response.json()
            return pull_requests_data


    async def main(self):
        # action_types = ["created", "opened", "labeled", "unlabeled", "edited", "closed", "assigned", "unassigned"]
        start_time = time.time()
        action_types = ["labeled"]
        engine = create_async_engine(get_postgres_uri(), echo=False, poolclass=NullPool)
        async_session = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
        issue_handler = IssuesHandler()
        pr_handler = Pull_requestHandler()
        jwt_token = self.jwt_generator.__call__()
        # jwt_token = self.get_github_jwt()
        jwt_headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {jwt_token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        installations = await self.get_installations(jwt_headers)
        # access_tokens = {installation.get('id'): await self.get_access_token(jwt_headers, installation.get('id')) for
        #                 installation in installations}
        # print(access_tokens)
        all_issue_ids = set()
        all_comment_ids = set()
        all_pr_id = set()

        original_issue = await self.postgres_client.readAll("issues")
        original_prs = await self.postgres_client.readAll("pr_history")
        original_orgs = await self.postgres_client.readAll("community_orgs")


        for installation in installations:
            time.sleep(5)
            token = await self.get_access_token(jwt_headers, installation.get('id'))
           
            repos = await self.get_repos(token)
            for repo in repos:
                repo_name = repo.get("full_name")
                issues = await self.get_issues(token, repo_name)

                #process issues
                issues = await self.process_cron_issues(issues, all_issue_ids, all_comment_ids)
                #process issue_comments

                #process prs
                pull_requests = await self.get_pull_requests(token, repo_name)

                await self.process_cron_prs(pull_requests, all_pr_id)
                print('finished cron')


        #purge remaining issues, comments
        await self.purge_issues_comments(all_issue_ids, all_comment_ids)


        new_issues_length = len(all_issue_ids)
        new_prs_length = len(all_pr_id)
        new_orgs = await self.postgres_client.readAll("community_orgs")
        new_orgs_length = len(new_orgs)
        #share report

        original_issue_length = len(original_issue)
        original_pr_length = len(original_prs)
        original_orgs_length = len(original_orgs)
        end_time = time.time()

        time_taken = end_time - start_time
        await self.send_discord_report(original_issue_length, new_issues_length, original_pr_length, new_prs_length, original_orgs_length, new_orgs_length, time_taken)

        """ Need to use pull_request_handler from handlers """
        """ Only closed PRs need to be updated with points"""
        """ All issues need to be updated? - Yes
            To update issues - use , log_user_activity class
        """
        """ Do we have a separate table for organisations - Yes"""
        """ Mentor's data is in body - Body will always be there in a closed Issue/PR"""



    async def process_cron_issues(self, issues, issue_ids_list, all_comment_ids):
        try:
            issue_handler = IssuesHandler()
            
            for issue in issues:
                time.sleep(5)
                issue_ids_list.add(issue["id"])
                data={
                "action":f'{issue["state"]}ed', 
                "issue":issue
                }
                await issue_handler.handle_event(data=data, postgres_client='client')

                #process issue comments
                all_comments = await self.get_issue_comments(issue["comments_url"])
                self.process_cron_issue_comments(all_comments, all_comment_ids)
            
            return 'issues processed'

        except Exception as e:
            print('Exception occured in process_cron_issues ', e)
            return e

    async def get_issue_data(self, issue_url):
        try:
            GITHUB_TOKEN = os.getenv('API_TOKEN')
            headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            
            async with httpx.AsyncClient() as client:
                issue_response = await client.get(issue_url, headers=headers)
                if issue_response.status_code == 200:
                    
                    issue_details = issue_response.json()
                    issue_id = issue_details["id"]
                    return issue_id
                
            return None
        except Exception as e:
            print('Exception occured while getting issue data ', e)
            return None
 

    async def process_cron_issue_comments(self, all_comments, all_comment_ids):
        try:
            for comment in all_comments:
                time.sleep(5)
                all_comment_ids.add(comment["id"])

                issue_id = await self.get_issue_data(comment['issue_url'])
                comment_data = {
                'url':comment["url"],
                'html_url':comment['html_url'],
                'issue_url':comment['issue_url'],
                'issue_id': issue_id,
                'comment_id': comment['id'],
                'node_id':comment['node_id'],
                'commented_by':comment['user']['login'],
                'commented_by_id':comment['user']['id'],
                'content':comment['body'],
                'reactions_url':comment['reactions']['url'],
                'ticket_url':comment['issue_url'],
                'id':comment['id'],
                'created_at':str(datetime.now()),
                'updated_at':str(datetime.now()) 
            }

            print('comments data ', comment_data)
                        
            is_comment_present = await self.postgres_client.get_data('id', 'ticket_comments', comment['id'])
            if is_comment_present:
                save_data = await self.postgres_client.add_data(comment_data,"ticket_comments")
            else:
                save_data = await self.postgres_client.update_data(comment_data, "id", "ticket_comments")

        except Exception as e:
            print('Exception occured in process_cron_issue_comments ', e)
            return e


    async def process_cron_prs(self, pull_requests, all_pr_id):
        try:
            pr_handler = Pull_requestHandler()
            for pr in pull_requests:
                time.sleep(5)
                all_pr_id.add(pr["id"])
                await pr_handler.handle_event(
                    data={"action": "closed" if pr["state"] == "close" else "opened",
                            "pull_request": pr},
                    dummy_ps_client='async_session')
                
            return 'processed pr'
                    
        except Exception as e:
            print('Exception occured in process_cron_issue_comments', e)
            return e

    async def purge_issues_comments(self, issue_ids, comment_ids):
        try:
            all_issue_ids_db = await self.postgres_client.read("issues", select_columns="issue_id")
            all_comment_ids_db = await self.postgres_client.read("ticket_comments", select_columns="comment_id")

            for issue_id in all_issue_ids_db:
                is_present = {i['issue_id'] for i in issue_ids}
                if not is_present:
                    await self.postgres_client.delete("issue_contributors","issue_id",issue_id)
                    await self.postgres_client.delete("issue_mentors","issue_id",issue_id)
                    # Delete Ticket
                    await self.postgres_client.delete("issues","id",issue_id)
                    print(f'issue with issue_id {issue_id} purged')

            for comment_id in all_comment_ids_db:
                is_comment_present = {c['comment_id'] for c in comment_ids}
                if not is_comment_present:
                    await self.postgres_client.delete("ticket_comments","comment_id",comment_id)
                    print(f'comment with comment_id {comment_id} purged')
        except Exception as e:
            print('exception occured while purging data ', e)
            return 'Error occured'


    async def send_discord_report(self, original_issue_length, new_issues_length, original_pr_length, new_prs_length, original_orgs_length, new_orgs_length, time_taken):
        try:
            DISCORD_WEBHOOK_URL = os.getenv("CRON_DISCORD_WEBHOOK_URL")
            if not DISCORD_WEBHOOK_URL:
                raise ValueError("DISCORD_WEBHOOK_URL is not set in environment variables.")
            
            message = 'Cron finished execution'

            report = (
                        f"total time taken: {time_taken:.2f},\n"
                        f"total original issues: {original_issue_length},\n"
                        f"total new issues: {new_issues_length},\n"
                        f"delta issues: {new_issues_length - original_issue_length},\n"
                        f"total original PRs: {original_pr_length},\n"
                        f"total new PRs: {new_prs_length},\n"
                        f"delta PRs: {new_prs_length - original_pr_length},\n"
                        f"total original orgs: {original_orgs_length},\n"
                        f"total new orgs: {new_orgs_length},\n"
                        f"delta orgs: {new_orgs_length - original_orgs_length}"
                    )
            
            data = {
                "content": message,
                "embeds": [
                    {
                        "title": "Cron Job Report",
                        "description": report,
                        "color": 3066993  # Green
                    }
                ]
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(DISCORD_WEBHOOK_URL, json=data)
                if response.status_code == 204:
                    print("Update successfully sent to Discord!")
                else:
                    print(f"Failed to send update to Discord. Status: {response.status_code}, Response: {response.text}")

        except Exception as e:
            print('Exception occured while sending report to discord ', e)
            return 'Exception occured'



if __name__ == '__main__':
    cronjob = CronJob()
    asyncio.run(cronjob.main())