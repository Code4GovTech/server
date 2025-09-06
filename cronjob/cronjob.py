import asyncio
from datetime import datetime, timezone, timedelta
import httpx
import jwt
# from jwt import JWT
import os
from dotenv import load_dotenv
import sys
import time

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from utils.jwt_generator import GenerateJWT
from utils.logging_file import logger
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
            logger.error(f"In get_github_jwt: {e}")
            return None


    async def get_rate_limits(self, token: str):
        rate_limit_url = "https://api.github.com/rate_limit"
        token_headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        async with httpx.AsyncClient() as client:
            rate_limit_resp = await client.get(rate_limit_url, headers=token_headers)
            return rate_limit_resp.json()


    async def get_installations(self, token_headers: dict):
        async with httpx.AsyncClient() as client:
            get_installations_url = 'https://api.github.com/app/installations'
            installations_response = await client.get(get_installations_url, headers=token_headers)
            print(installations_response.status_code, installations_response.text)

            if installations_response.status_code == 200:
                return installations_response.json()
            elif installations_response.status_code == 401:
                if installations_response.json().get("message",
                                                    None) == '\'Expiration time\' claim (\'exp\') must be a numeric value representing the future time at which the assertion expires':

                    logger.info("JWT expired at get_installation stage")
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

                    logger.info("JWT expired at get_access_token stage")
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


    async def get_issues(self, token: str, since: datetime, repo_fullname: str, to_date=None):
        page = 1
        all_issues = []
        while True:
            get_issue_url = f"https://api.github.com/repos/{repo_fullname}/issues?state=all&per_page=100&page={page}"
            token_headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28"
            }

            payload = {
                "labels": "c4gt community",
                "since": since.isoformat(),
                "direction": "asc"
            }
            async with httpx.AsyncClient() as client:
                issues_response = await client.get(url=get_issue_url, headers=token_headers, params=payload)
                page_issues = issues_response.json()

                # Filter based on created_at if to_date is provided
                if to_date:
                    page_issues = [issue for issue in page_issues if
                                   datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00')) <= to_date]

                if len(page_issues) > 0:
                    all_issues += page_issues
                    page += 1
                else:
                    break

                rate_limit = await self.get_rate_limits(token)
                print(rate_limit)

        return all_issues

    async def get_issue_comments(self, issue_comment_url, since: datetime, to_date=None, **kwargs):
        page = 1

        all_comments = []
        token = kwargs.get("token", None)
        while True:
            comments_url = f"{issue_comment_url}?state=all&page={page}&per_page=100"
            payload = {
                "since": since.isoformat(),
                "direction": "asc"
            }

            async with httpx.AsyncClient() as client:
                if token:
                    token_headers = {
                        "Accept": "application/vnd.github+json",
                        "Authorization": f"Bearer {token}",
                        "X-GitHub-Api-Version": "2022-11-28"
                    }
                    response = await client.get(url=comments_url, headers=token_headers, params=payload)
                else:
                    response = await client.get(url=comments_url, params=payload)

                issue_comments_data = response.json()

                # Filter based on created_at if to_date is provided
                if to_date:
                    issue_comments_data = [
                        comment for comment in issue_comments_data
                        if datetime.fromisoformat(comment['created_at'].replace('Z', '+00:00')) <= to_date
                    ]

                if len(issue_comments_data) > 0:
                    all_comments += issue_comments_data
                    page += 1
                else:
                    break

        return all_comments

    async def get_pull_requests(self, token: str, repo_fullname, since: datetime):
        page = 1
        all_prs = []
        while True:
            get_pull_requests_url = f"https://api.github.com/repos/{repo_fullname}/pulls?state=all&page={page}&per_page=100"
            token_headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            payload = {"since": since.isoformat()}
            async with httpx.AsyncClient() as client:
                pull_requests_response = await client.get(url=get_pull_requests_url,
                                                          headers=token_headers,
                                                          params=payload
                                                        )
                pull_requests_data = pull_requests_response.json()
                if len(pull_requests_data)>0:
                    page += 1
                    all_prs += pull_requests_data
                else:
                    break
        return all_prs


    async def main(self, from_date=None, to_date=None):
        start_time = time.time()
        logger.info(f"Cron triggered")
        engine = create_async_engine(get_postgres_uri(), echo=False, poolclass=NullPool)
        jwt_token = self.jwt_generator.__call__()

        jwt_headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {jwt_token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        installations = await self.get_installations(jwt_headers)
        access_tokens = {installation.get('id'): await self.get_access_token(jwt_headers, installation.get('id')) for
                         installation in installations}


        all_issue_ids = set()
        all_comment_ids = set()
        all_pr_id = set()

        # Parse date params
        since = datetime.now() - timedelta(days=1)  # Default to 1 day before
        if from_date:
            since = datetime.fromisoformat(from_date)
        to_date = datetime.fromisoformat(to_date).replace(tzinfo=timezone.utc) if to_date else None

        for installation in installations:
            logger.info(f"Installation: ", installation)
            token = access_tokens.get(installation.get('id'))
            if not token:
                print(f"Error in installation {installation.get('id')}")
                continue

            repos = await self.get_repos(token)
            for repo in repos:
                repo_name = repo.get("full_name")
                logger.info(f"Repository: {repo_name}")
                issues = await self.get_issues(token, since, repo_name, to_date)

                # Pass from_date and to_date to process_cron_issues
                processed_issues = await self.process_cron_issues(
                    issues,
                    all_issue_ids,
                    all_comment_ids,
                    from_date=since,
                    to_date=to_date,
                    token=token
                )
                # pull_requests = await self.get_pull_requests(token, repo_name, since)
                # processed_prs = await self.process_cron_prs(pull_requests, all_pr_id)

        await self.purge_issues_comments(all_issue_ids, all_comment_ids)

        end_time = time.time()
        time_taken = end_time - start_time
        # await self.send_discord_report(
        #     len(original_issue),
        #     len(all_issue_ids),
        #     len(original_prs),
        #     len(all_pr_id),
        #     len(original_orgs),
        #     len(await self.postgres_client.readAll("community_orgs")),
        #     time_taken
        # )

    async def process_cron_issues(self, issues, issue_ids_list, all_comment_ids, from_date=None, to_date=None,
                                  **kwargs):
        try:
            token = kwargs.get("token", None)
            issue_handler = IssuesHandler()

            for issue in issues:
                try:
                    logger.info(f"Issue: {issue.get('html_url')}")
                    issue_ids_list.add(issue["id"])
                    state = f'{issue["state"]}ed'
                    state = state.replace('eded', 'ed')
                    data = {
                        "action": state,
                        "issue": issue
                    }
                    if token is not None:
                        await issue_handler.handle_event(
                            data=data,
                            postgres_client='client',
                            token=token
                        )
                    else:
                        await issue_handler.handle_event(
                            data=data,
                            postgres_client='client'
                        )

                    # Process issue comments with from_date and to_date
                    since = from_date or (datetime.now() - timedelta(days=1))
                    all_comments = await self.get_issue_comments(
                        issue["comments_url"],
                        since=since,
                        to_date=to_date,
                        token=token
                    )
                    time.sleep(1)
                    processed_comments = await self.process_cron_issue_comments(
                        issue, all_comments, all_comment_ids
                    )

                except Exception as e:
                    print("Exception in issue - ", issue, e)
                    continue

            return 'issues processed'

        except Exception as e:
            print('Exception occurred in process_cron_issues:', e)
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
 

    async def process_cron_issue_comments(self, issue, all_comments, all_comment_ids):
        try:
            print('inside cron comments')
            for comment in all_comments:
                # time.sleep(5)
                all_comment_ids.add(comment["id"])

                issue_id = issue["id"]
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

                if is_comment_present is None or len(is_comment_present) == 0:
                    save_data = await self.postgres_client.add_data(comment_data,"ticket_comments")
                else:
                    save_data = await self.postgres_client.update_data(comment_data, "id", "ticket_comments")
                print(save_data)
            return True
        except Exception as e:
            print('Exception occured in process_cron_issue_comments ', e)
            return e


    async def process_cron_prs(self, pull_requests, all_pr_id):
        try:
            pr_handler = Pull_requestHandler()
            for pr in pull_requests:
                try:
                    logger.info(f"PR: {pr.get('html_url')}")
                    all_pr_id.add(pr["id"])
                    await pr_handler.handle_event(
                        data={"action": "closed" if pr["state"] == "close" else "opened",
                                "pull_request": pr},
                        dummy_ps_client='async_session')
                except Exception as e:
                    print("Error in processing pr")
                
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
    from_date= "2025-03-01T00:00:00"
    to_date = "2025-03-11T00:00:00"
    asyncio.run(cronjob.main(from_date,to_date))
