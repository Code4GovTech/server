from utils.github_api import GithubAPI
from utils.db import SupabaseInterface
import aiohttp, sys
from utils.runtime_vars import MARKDOWN_TEMPLATE_HEADERS

headerMessages = {
    "Product Name": "Product Name - Please add a heading called Product Name and mention the name of the product below it. ",
    "Project": "Project/Project Name",
    "Project Name": "Project/Project Name",
    "Organization Name": "Organization Name",
    "Domain": "Domain - Area of governance",
    "Tech Skills Needed": "Tech Skills Needed - Please add relevant tech skills ",
    "Mentor(s)": "Mentors(s) Please tag the relevant mentors on the ticket",
    "Complexity": "Complexity - Please mention the complexity only as High/Medium/Low",
    "Category": "Category - Please add one or more of these options [CI/CD], [Integrations], [Performance Improvement], [Security], [UI/UX/Design], [Bug], [Feature], [Documentation], [Deployment], [Test], [PoC]",
    "Sub Category": "Sub-Category - Please mention the sub-category if any for the ticket",
    "Invalid Complexity": "Complexity must be High/Medium/Low"
}

class TicketFeedbackHandler:
    def __init__(self):
        return
    
    def evaluateDict(self,md_dict):
            missing_headers = []
            for header in MARKDOWN_TEMPLATE_HEADERS:
                if header not in md_dict.keys():
                    missing_headers.append(header)
            if ("Product" in missing_headers or "Product Name" in missing_headers) and not ("Product" in missing_headers and "Product Name" in missing_headers):
                if "Product"in missing_headers:
                    missing_headers.remove("Product")
                elif"Product Name" in missing_headers:
                    missing_headers.remove("Product Name")

            #Project Name is in the template but project name is being taken from the title of the ticket
            if "Project"in missing_headers:
                missing_headers.remove("Project")
            if "Project Name" in missing_headers:
                missing_headers.remove("Project Name")
            return missing_headers
    
    def feedBackMessageCreator(self, markdown_dict):
        missing_headers = self.evaluateDict(markdown_dict)
        if "Product" in missing_headers and "Product Name" in missing_headers:
            missing_headers.remove("Product")
        mandatoryHeaders = ''
        optionalHeaders = ''
        heads = ''
        for header in missing_headers:
            if header in ['Product Name', 'Complexity', 'Category', 'Mentor(s)', 'Tech Skills Needed']:
                mandatoryHeaders+=f'- {headerMessages[header]}\n'
            else:
                optionalHeaders+=f'- {headerMessages[header]}\n'
        if markdown_dict.get("Complexity") and markdown_dict.get("Complexity").lower() not in ['low', 'medium', 'high']:
            mandatoryHeaders+=f'- {headerMessages["Invalid Complexity"]}\n' 
        if 'Mentor(s)' in markdown_dict and not markdown_dict["Mentor(s)"]:
            mandatoryHeaders+=f'-Please make sure the Mentor(s) field is not empty\n'
        mandatoryHeaderText = f'''\nMandatory Details - The following details essential to submit tickets to C4GT Community Program are missing. Please add them!
{mandatoryHeaders}\nWithout these details, the ticket cannot be listed on the C4GT Community Listing.\n'''
        optionalHeaderText = f'''\nImportant Details -  These following details are helpful for contributors to effectively identify and contribute to tickets. 
{optionalHeaders}\n'''
        body = f'''Hi! {mandatoryHeaderText if mandatoryHeaders else ''}{optionalHeaderText if optionalHeaders else ''}
Please update the ticket
        '''

        return body
    
    async def createComment(self, owner, repo, issue_number, markdown_dict):
        token = await GithubAPI().authenticate_app_as_installation(repo_owner=owner)
        print('token checked ', token)
        print('creating comments')

        url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments'
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {token}',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        data = {
            'body': f'{self.feedBackMessageCreator(markdown_dict=markdown_dict)}'
        }
        print('posting data')

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
        print('token checked ', token)
        url = f'https://api.github.com/repos/{owner}/{repo}/issues/comments/{comment_id}'
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {token}',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        data = {
            'body': f'{self.feedBackMessageCreator(markdown_dict)}'
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

        
