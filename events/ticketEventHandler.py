# Tickets are created, edited and deleted
# Comments are created edited and deleted

import aiohttp
import os, sys
from utils.db import SupabaseInterface
from utils.markdown_handler import MarkdownHeaders
from utils.github_api import GithubAPI
from utils.jwt_generator import GenerateJWT
from aiographql.client import GraphQLClient, GraphQLRequest

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

async def get_closing_pr(repo, owner, num):
    client = GraphQLClient(
    endpoint="https://api.github.com/graphql",
    headers={"Authorization": f"Bearer {os.getenv('GithubPAT')}"},
    )
    request = GraphQLRequest(
    query=f"""
query {{
  repository(name: "{repo}", owner: "{owner}") {{
    issue(number: {num}) {{
      timelineItems(itemTypes: CLOSED_EVENT, last: 1) {{
        nodes {{
          ... on ClosedEvent {{
            createdAt
            closer {{
               __typename
              ... on PullRequest {{
                baseRefName
                url
                baseRepository {{
                  nameWithOwner
                }}
                headRefName
                headRepository {{
                  nameWithOwner
                }}
              }}
            }}
          }}
        }}
      }}
    }}
  }}
}}
    """
    )
    response = await client.query(request=request)
    data = response.data
    if data["repository"]["issue"]["timelineItems"]["nodes"][0]["closer"]:
        if data["repository"]["issue"]["timelineItems"]["nodes"][0]["closer"]["__typename"] == "PullRequest":
            return data["repository"]["issue"]["timelineItems"]["nodes"][0]["closer"]["url"]
        else: 
            return None

class TicketEventHandler:
    def __init__(self):
        self.supabase_client = SupabaseInterface()
        self.ticket_points = {
                        "High": 30,
                        "Medium":20,
                        "Low":10,
                        "Unknown":10
                    }
        return
    
    async def onTicketCreate(self, eventData):
        if not eventData.get("comment"):
            issue = eventData["issue"]
            if any(label["name"] == "C4GT Community" for label in issue["labels"] ):
                markdown_contents = MarkdownHeaders().flattenAndParse(eventData["issue"]["body"])
                ticket_data = {
                            "name":issue["title"],     #name of ticket
                            "product":issue["repository_url"].split('/')[-1],
                            "complexity":markdown_contents["Complexity"] if markdown_contents.get("Complexity") else None ,
                            "project_category":markdown_contents["Category"].split(',') if markdown_contents.get("Category") else None,
                            "project_sub_category":markdown_contents["Sub Category"].split(',') if markdown_contents.get("Sub Category") else None,
                            "reqd_skills":markdown_contents["Tech Skills Needed"] if markdown_contents.get("Tech Skills Needed") else None,
                            "issue_id":issue["id"],
                            "status": issue["state"],
                            "api_endpoint_url":issue["url"],
                            "url": issue["html_url"],
                            "ticket_points":self.ticket_points[markdown_contents["Complexity"]] if markdown_contents.get("Complexity") else None,
                            "mentors": [github_handle[1:] for github_handle in markdown_contents["Mentor(s)"].split(' ')] if markdown_contents.get("Mentor(s)") else None
                        }
                print(ticket_data, file=sys.stderr)
                print(self.supabase_client.record_created_ticket(data=ticket_data), file=sys.stderr)
        return eventData

    async def onTicketEdit(self, eventData):
        issue = eventData["issue"]
        if eventData["action"] == "unlabeled":
            if (not issue["labels"]) or (not any(label["name"] == "C4GT Community" for label in issue["labels"] )):
                # Delete Ticket
                self.supabase_client.deleteTicket(issue["id"])
        markdown_contents = MarkdownHeaders().flattenAndParse(issue["body"])
        print(markdown_contents)
        ticket_data = {
                        "name":issue["title"],     #name of ticket
                        "product":issue["repository_url"].split('/')[-1],
                        "complexity":markdown_contents["Complexity"] if markdown_contents.get("Complexity") else None ,
                        "project_category":markdown_contents["Category"].split(',') if markdown_contents.get("Category") else None,
                        "project_sub_category":markdown_contents["Sub Category"].split(',') if markdown_contents.get("Sub Category") else None,
                        "reqd_skills":markdown_contents["Tech Skills Needed"] if markdown_contents.get("Tech Skills Needed") else None,
                        "issue_id":issue["id"],
                        "status": issue["state"],
                        "api_endpoint_url":issue["url"],
                        "url": issue["html_url"],
                        "ticket_points":self.ticket_points[markdown_contents["Complexity"]] if markdown_contents.get("Complexity") else None,
                        "mentors": [github_handle[1:] for github_handle in markdown_contents["Mentor(s)"].split(' ')] if markdown_contents.get("Mentor(s)") else None
                    }
        print(ticket_data, file=sys.stderr)
        print(self.supabase_client.update_recorded_ticket(data=ticket_data))

        return eventData
    async def onTicketClose(self, eventData):
        issue = eventData["issue"]
        [repo, owner, issue_number] = [issue["url"].split('/')[-3],issue["url"].split('/')[-4],issue["url"].split('/')[-1]]
        pull_request_url = await get_closing_pr(repo, owner, issue_number)
        if pull_request_url:
            pull_number=pull_request_url.split('/')[-1]
            pull_data = await get_pull_request(owner, repo, pull_number)
            self.supabase_client.addPr(pull_data)
        return
    
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
                                # print(repo, file=sys.stderr)
                                data = await get_comments(repo)
                                if data:
                                    comments+=data
                    
                    count = 0
                    for comment in comments:
                        print(comment)
                        if comment["user"]["login"] == "c4gt-community-support[bot]":
                            count+=1
                    print(count, file=sys.stderr)
                    return {}
                    

                    
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
    

class CommentEventHandler:
    def __init__():
        return

# from events.ticketEventHandler import TicketEventHandler
# testEvent = {
#   "action": "opened",
#   "issue": {
#     "url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/issues/53",
#     "repository_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app",
#     "labels_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/issues/53/labels{/name}",
#     "comments_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/issues/53/comments",
#     "events_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/issues/53/events",
#     "html_url": "https://github.com/KDwevedi/testing_for_github_app/issues/53",
#     "id": 1766723561,
#     "node_id": "I_kwDOJvNYv85pTg_p",
#     "number": 53,
#     "title": "[C4GT] Test Issue",
#     "user": {
#       "login": "KDwevedi",
#       "id": 74085496,
#       "node_id": "MDQ6VXNlcjc0MDg1NDk2",
#       "avatar_url": "https://avatars.githubusercontent.com/u/74085496?v=4",
#       "gravatar_id": "",
#       "url": "https://api.github.com/users/KDwevedi",
#       "html_url": "https://github.com/KDwevedi",
#       "followers_url": "https://api.github.com/users/KDwevedi/followers",
#       "following_url": "https://api.github.com/users/KDwevedi/following{/other_user}",
#       "gists_url": "https://api.github.com/users/KDwevedi/gists{/gist_id}",
#       "starred_url": "https://api.github.com/users/KDwevedi/starred{/owner}{/repo}",
#       "subscriptions_url": "https://api.github.com/users/KDwevedi/subscriptions",
#       "organizations_url": "https://api.github.com/users/KDwevedi/orgs",
#       "repos_url": "https://api.github.com/users/KDwevedi/repos",
#       "events_url": "https://api.github.com/users/KDwevedi/events{/privacy}",
#       "received_events_url": "https://api.github.com/users/KDwevedi/received_events",
#       "type": "User",
#       "site_admin": False
#     },
#     "labels": [
#       {
#         "id": 5618130256,
#         "node_id": "LA_kwDOJvNYv88AAAABTt3dUA",
#         "url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/labels/bug",
#         "name": "bug",
#         "color": "d73a4a",
#         "default": True,
#         "description": "Something isn't working"
#       },
#       {
#         "id": 5618130272,
#         "node_id": "LA_kwDOJvNYv88AAAABTt3dYA",
#         "url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/labels/help%20wanted",
#         "name": "help wanted",
#         "color": "008672",
#         "default": True,
#         "description": "Extra attention is needed"
#       },
#       {
#         "id": 5618368045,
#         "node_id": "LA_kwDOJvNYv88AAAABTuF-LQ",
#         "url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/labels/C4GT%20Community",
#         "name": "C4GT Community",
#         "color": "3C6698",
#         "default": False,
#         "description": "C4GT Community Ticket"
#       }
#     ],
#     "state": "open",
#     "locked": False,
#     "assignee": None,
#     "assignees": [],
#     "milestone": None,
#     "comments": 0,
#     "created_at": "2023-06-21T05:36:22Z",
#     "updated_at": "2023-06-21T05:36:22Z",
#     "closed_at": None,
#     "author_association": "OWNER",
#     "active_lock_reason": None,
#     "body": "## Description\r\nDesc\r\n\r\n## Goals\r\n- [ ] [Goal 1]\r\n- [ ] [Goal 2]\r\n- [ ] [Goal 3]\r\n- [ ] [Goal 4]\r\n- [ ] [Goal 5]\r\n\r\n## Expected Outcome\r\n[Describe in detail what the final product or result should look like and how it should behave.]\r\n\r\n## Acceptance Criteria\r\n- [ ] [Criteria 1]\r\n- [ ] [Criteria 2]\r\n- [ ] [Criteria 3]\r\n- [ ] [Criteria 4]\r\n- [ ] [Criteria 5]\r\n\r\n## Implementation Details\r\n[List any technical details about the proposed implementation, including any specific technologies that will be used.]\r\n\r\n## Mockups / Wireframes\r\n[Include links to any visual aids, mockups, wireframes, or diagrams that help illustrate what the final product should look like. This is not always necessary, but can be very helpful in many cases.]\r\n\r\n---\r\n\r\n### Project\r\nProject\r\n\r\n### Organization Name:\r\nOrganisation\r\n\r\n### Domain\r\nE-Governance\r\n\r\n### Tech Skills Needed:\r\nReactJS\r\n\r\n### Mentor(s)\r\n@KDwevedi \r\n\r\n### Complexity\r\nMedium\r\n\r\n### Category\r\nPerformance Improvement\r\n\r\n### Sub Category\r\nAnalytics\r\n",
#     "reactions": {
#       "url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/issues/53/reactions",
#       "total_count": 0,
#       "+1": 0,
#       "-1": 0,
#       "laugh": 0,
#       "hooray": 0,
#       "confused": 0,
#       "heart": 0,
#       "rocket": 0,
#       "eyes": 0
#     },
#     "timeline_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/issues/53/timeline",
#     "performed_via_github_app": None,
#     "state_reason": None
#   },
#   "repository": {
#     "id": 653482175,
#     "node_id": "R_kgDOJvNYvw",
#     "name": "testing_for_github_app",
#     "full_name": "KDwevedi/testing_for_github_app",
#     "private": False,
#     "owner": {
#       "login": "KDwevedi",
#       "id": 74085496,
#       "node_id": "MDQ6VXNlcjc0MDg1NDk2",
#       "avatar_url": "https://avatars.githubusercontent.com/u/74085496?v=4",
#       "gravatar_id": "",
#       "url": "https://api.github.com/users/KDwevedi",
#       "html_url": "https://github.com/KDwevedi",
#       "followers_url": "https://api.github.com/users/KDwevedi/followers",
#       "following_url": "https://api.github.com/users/KDwevedi/following{/other_user}",
#       "gists_url": "https://api.github.com/users/KDwevedi/gists{/gist_id}",
#       "starred_url": "https://api.github.com/users/KDwevedi/starred{/owner}{/repo}",
#       "subscriptions_url": "https://api.github.com/users/KDwevedi/subscriptions",
#       "organizations_url": "https://api.github.com/users/KDwevedi/orgs",
#       "repos_url": "https://api.github.com/users/KDwevedi/repos",
#       "events_url": "https://api.github.com/users/KDwevedi/events{/privacy}",
#       "received_events_url": "https://api.github.com/users/KDwevedi/received_events",
#       "type": "User",
#       "site_admin": False
#     },
#     "html_url": "https://github.com/KDwevedi/testing_for_github_app",
#     "description": None,
#     "fork": False,
#     "url": "https://api.github.com/repos/KDwevedi/testing_for_github_app",
#     "forks_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/forks",
#     "keys_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/keys{/key_id}",
#     "collaborators_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/collaborators{/collaborator}",
#     "teams_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/teams",
#     "hooks_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/hooks",
#     "issue_events_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/issues/events{/number}",
#     "events_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/events",
#     "assignees_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/assignees{/user}",
#     "branches_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/branches{/branch}",
#     "tags_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/tags",
#     "blobs_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/git/blobs{/sha}",
#     "git_tags_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/git/tags{/sha}",
#     "git_refs_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/git/refs{/sha}",
#     "trees_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/git/trees{/sha}",
#     "statuses_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/statuses/{sha}",
#     "languages_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/languages",
#     "stargazers_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/stargazers",
#     "contributors_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/contributors",
#     "subscribers_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/subscribers",
#     "subscription_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/subscription",
#     "commits_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/commits{/sha}",
#     "git_commits_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/git/commits{/sha}",
#     "comments_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/comments{/number}",
#     "issue_comment_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/issues/comments{/number}",
#     "contents_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/contents/{+path}",
#     "compare_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/compare/{base}...{head}",
#     "merges_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/merges",
#     "archive_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/{archive_format}{/ref}",
#     "downloads_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/downloads",
#     "issues_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/issues{/number}",
#     "pulls_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/pulls{/number}",
#     "milestones_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/milestones{/number}",
#     "notifications_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/notifications{?since,all,participating}",
#     "labels_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/labels{/name}",
#     "releases_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/releases{/id}",
#     "deployments_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/deployments",
#     "created_at": "2023-06-14T06:28:22Z",
#     "updated_at": "2023-06-20T10:43:27Z",
#     "pushed_at": "2023-06-20T15:21:18Z",
#     "git_url": "git://github.com/KDwevedi/testing_for_github_app.git",
#     "ssh_url": "git@github.com:KDwevedi/testing_for_github_app.git",
#     "clone_url": "https://github.com/KDwevedi/testing_for_github_app.git",
#     "svn_url": "https://github.com/KDwevedi/testing_for_github_app",
#     "homepage": None,
#     "size": 36,
#     "stargazers_count": 0,
#     "watchers_count": 0,
#     "language": None,
#     "has_issues": True,
#     "has_projects": True,
#     "has_downloads": True,
#     "has_wiki": True,
#     "has_pages": False,
#     "has_discussions": False,
#     "forks_count": 0,
#     "mirror_url": None,
#     "archived": False,
#     "disabled": False,
#     "open_issues_count": 1,
#     "license": {
#       "key": "mit",
#       "name": "MIT License",
#       "spdx_id": "MIT",
#       "url": "https://api.github.com/licenses/mit",
#       "node_id": "MDc6TGljZW5zZTEz"
#     },
#     "allow_forking": True,
#     "is_template": False,
#     "web_commit_signoff_required": False,
#     "topics": [],
#     "visibility": "public",
#     "forks": 0,
#     "open_issues": 1,
#     "watchers": 0,
#     "default_branch": "main"
#   },
#   "sender": {
#     "login": "KDwevedi",
#     "id": 74085496,
#     "node_id": "MDQ6VXNlcjc0MDg1NDk2",
#     "avatar_url": "https://avatars.githubusercontent.com/u/74085496?v=4",
#     "gravatar_id": "",
#     "url": "https://api.github.com/users/KDwevedi",
#     "html_url": "https://github.com/KDwevedi",
#     "followers_url": "https://api.github.com/users/KDwevedi/followers",
#     "following_url": "https://api.github.com/users/KDwevedi/following{/other_user}",
#     "gists_url": "https://api.github.com/users/KDwevedi/gists{/gist_id}",
#     "starred_url": "https://api.github.com/users/KDwevedi/starred{/owner}{/repo}",
#     "subscriptions_url": "https://api.github.com/users/KDwevedi/subscriptions",
#     "organizations_url": "https://api.github.com/users/KDwevedi/orgs",
#     "repos_url": "https://api.github.com/users/KDwevedi/repos",
#     "events_url": "https://api.github.com/users/KDwevedi/events{/privacy}",
#     "received_events_url": "https://api.github.com/users/KDwevedi/received_events",
#     "type": "User",
#     "site_admin": False
#   },
#   "installation": {
#     "id": 38589024,
#     "node_id": "MDIzOkludGVncmF0aW9uSW5zdGFsbGF0aW9uMzg1ODkwMjQ="
#   }
# }
# TicketEventHandler().onTicketEdit(testEvent)
    
