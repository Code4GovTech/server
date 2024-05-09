from utils.github_api import GithubAPI
import aiohttp, sys,os,httpx
from utils.jwt_generator import GenerateJWT
from events.ticketFeedbackHandler import TicketFeedbackHandler



class GithubAdapter:
    def __init__(self):
        return
    
    async def get_calssroom_data(assignment_id,page):
        github_api_url = f'https://api.github.com/assignments/{assignment_id}/accepted_assignments?page={page}'
        
        # Define request headers
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': 'Bearer'+' '+ os.getenv('API_TOKEN'),
            'X-GitHub-Api-Version': '2022-11-28'
        }

        async with httpx.AsyncClient() as client:
            try:
                # Make the request to the GitHub API
                response = await client.get(github_api_url, headers=headers)
                # Check if the request was successful
                if response.status_code == 200:
                    # Return the response from the GitHub API
                    response,code = response.json(),200
                    
            except :
                response = [],400
                
            return response,code
    
    async def createComment(self, owner, repo, issue_number, markdown_dict):
        token = await GithubAPI().authenticate_app_as_installation(repo_owner=owner)

        url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments'
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {token}',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        data = {
            'body': f'{TicketFeedbackHandler.feedBackMessageCreator(markdown_dict=markdown_dict)}'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 201:
                    print('Comment created successfully.')
                    return await response.json()
                else:
                    print(f'Error creating comment. Status code: {response.status}', sys.stderr)
                    response_text = await response.text()
                    print(f'Response body: {response_text}', file=sys.stderr)
    
    async def updateComment(self, owner, repo, comment_id, markdown_dict):
        token = await GithubAPI().authenticate_app_as_installation(repo_owner=owner)
        url = f'https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}'
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {token}',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        data = {
            'body': f'{TicketFeedbackHandler.feedBackMessageCreator(markdown_dict)}'
        }

        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers, json=data) as response:
                if response.status == 200:
                    print('Comment updated successfully.')
                    return await response.json()
                else:
                    print(f'Error updating comment. Status code: {response.status}', file=sys.stderr)
                    response_text = await response.text()
                    print(f'Response body: {response_text}',file=sys.stderr)
    
    
    async def deleteComment(self, owner, repo, comment_id):
            token = await GithubAPI().authenticate_app_as_installation(repo_owner=owner)
            url = f'https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}'
            headers = {
                'Accept': 'application/vnd.github+json',
                'Authorization': f'Bearer {token}',
                'X-GitHub-Api-Version': '2022-11-28'
            }

            async with aiohttp.ClientSession() as session:
                async with session.delete(url, headers=headers) as response:
                    if response.status == 204:
                        print('Comment deleted successfully.')
                    else:
                        print(f'Error deleting comment. Status code: {response.status}', file=sys.stderr)
                        response_text = await response.text()
                        print(f'Response body: {response_text}', file=sys.stderr)
    async def bot_comments(self):

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
                    
                    
        
