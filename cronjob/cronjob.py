import asyncio
from datetime import datetime, timezone, timedelta
import httpx
import jwt
import os
from dotenv import load_dotenv
import logging

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from handlers.issues_handler import IssuesHandler
from handlers.pull_request_handler import Pull_requestHandler
from shared_migrations.db.server import get_postgres_uri

load_dotenv()


def get_github_jwt():
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


async def get_rate_limits(token_headers: dict):
    rate_limit_url = "https://api.github.com/rate_limit"
    async with httpx.AsyncClient() as client:
        rate_limit_resp = await client.get(rate_limit_url, headers=token_headers)
        return rate_limit_resp.json()


async def get_installations(token_headers: dict):
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


async def get_access_token(token_headers: dict, installation_id: str):
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


async def get_repos(token: str):
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


async def get_issues(token: str, repo_fullname):
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


async def get_pull_requests(token: str, repo_fullname):
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


async def main():
    # action_types = ["created", "opened", "labeled", "unlabeled", "edited", "closed", "assigned", "unassigned"]
    action_types = ["labeled"]
    engine = create_async_engine(get_postgres_uri(), echo=False, poolclass=NullPool)
    async_session = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
    issue_handler = IssuesHandler()
    pr_handler = Pull_requestHandler()
    jwt_token = get_github_jwt()
    jwt_headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {jwt_token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    installations = await get_installations(jwt_headers)
    access_tokens = {installation.get('id'): await get_access_token(jwt_headers, installation.get('id')) for
                     installation in installations}
    for token in access_tokens.values():
        repos = await get_repos(token)
        for repo in repos:
            repo_name = repo.get("full_name")
            issues = await get_issues(token, repo_name)
            issue_numbers = [issue.get('number') for issue in issues]
            issues = {issue["number"]: issue for issue in issues}

            if not issue_numbers:
                continue
            pull_requests = await get_pull_requests(token, repo_name)
            for pr in pull_requests:
                if pr.get('number') in issue_numbers:
                    print(pr)
                    for action in action_types:
                        try:
                            await issue_handler.handle_event(data={"action": action,
                                                                   "issue": issues[pr["number"]]},
                                                             postgres_client=async_session)
                        except:
                            pass
                    try:
                        await pr_handler.handle_event(
                            data={"action": "closed" if pr["state"] == "closed" else "opened",
                                  "pull_request": pr},
                            dummy_ps_client=async_session)
                    except:
                        pass

                    """ Need to use pull_request_handler from handlers """
                    """ Only closed PRs need to be updated with points"""
                    """ All issues need to be updated? - Yes
                        To update issues - use , log_user_activity class
                    """
                    """ Do we have a separate table for organisations - Yes"""
                    """ Mentor's data is in body - Body will always be there in a closed Issue/PR"""


if __name__ == '__main__':
    asyncio.run(main())
