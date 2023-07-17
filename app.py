from quart import Quart, redirect, render_template, request
import aiohttp, asyncio
import dotenv, os, json, urllib, sys, dateutil, datetime
from utils.db import SupabaseInterface
from events.ticketEventHandler import TicketEventHandler
from events.ticketFeedbackHandler import TicketFeedbackHandler
from githubdatapipeline.pull_request.scraper import getNewPRs
from githubdatapipeline.pull_request.processor import PrProcessor
from githubdatapipeline.issues.destination import recordIssue

fpath = os.path.join(os.path.dirname(__file__), 'utils')
sys.path.append(fpath)

dotenv.load_dotenv(".env")

app = Quart(__name__)
app.config['TESTING']= True

async def get_github_data(code, discord_id):
    github_url_for_access_token = 'https://github.com/login/oauth/access_token'
    data = {
        "client_id": os.getenv("GITHUB_CLIENT_ID"),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
        "code": code
    }
    headers = {
        "Accept": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(github_url_for_access_token, data=data, headers=headers) as response:
            r = await response.json()
            auth_token = (r)["access_token"]
            headers = {
                "Authorization": f"Bearer {auth_token}"
            }
            async with session.get("https://api.github.com/user", headers=headers) as user_response:
                user = await user_response.json()
                github_id = user["id"]
                github_username = user["login"]

                # Fetching user's private emails
                if "user:email" in r["scope"]:
                    async with session.get("https://api.github.com/user/emails", headers=headers) as email_response:
                        emails = await email_response.json()
                        private_emails = [email["email"] for email in emails if email["verified"]]
                else:
                    private_emails = []

                user_data = {
                    "discord_id": int(discord_id),
                    "github_id": github_id,
                    "github_url": f"https://github.com/{github_username}",
                    "email": ','.join(private_emails)
                }
                return user_data
            
async def comment_cleaner():
    while True:
        await asyncio.sleep(5)
        comments = SupabaseInterface().readAll("app_comments")
        for comment in comments:
            utc_now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
            update_time = dateutil.parser.parse(comment["updated_at"])
            if utc_now - update_time >= datetime.timedelta(minutes=15):
                url_components = comment["api_url"].split("/")
                owner = url_components[-5]
                repo = url_components[-4]
                comment_id = comment["comment_id"]
                issue_id = comment["issue_id"]
                comment = await TicketFeedbackHandler().deleteComment(owner, repo, comment_id)
                print(f"Print Delete Task,{comment}", file=sys.stderr)
                print(SupabaseInterface().deleteComment(issue_id))



# @app.before_serving
# async def startup():
#     app.add_background_task(comment_cleaner)

@app.route("/")
async def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/misc_actions")
async def addIssues():
    prs = SupabaseInterface().readAll("mentorship_program_pull_request")
    tickets = SupabaseInterface().readAll("mentorship_program_tickets")
    ticketUrls = [ticket["html_url"] for ticket in tickets]
    for pr in prs:
        if pr.get("body"):
            issues = PrProcessor().getLinkedIssues(pr)
            for issue in issues:
                if pr["repository_url"]+f'/issues/{issue}' in ticketUrls:
                    SupabaseInterface().update("mentorship_program_pull_request", {"linked_ticket":pr["repository_url"]+f'/issues/{issue}' }, "pr_id", pr["pr_id"])
    return "Hello World"
        

    # await getNewPRs()
    

@app.route("/already_authenticated")
async def isAuthenticated():
    return await render_template('success.html'), {"Refresh": f'2; url=https://discord.com/channels/{os.getenv("DISCORD_SERVER_ID")}'}

@app.route("/authenticate/<discord_userdata>")
async def authenticate(discord_userdata):

    redirect_uri = urllib.parse.quote(f'{os.getenv("HOST")}/register/{discord_userdata}')
    # print(redirect_uri)
    github_auth_url = f'https://github.com/login/oauth/authorize?client_id={os.getenv("GITHUB_CLIENT_ID")}&redirect_uri={redirect_uri}&scope=user:email'
    # print(github_auth_url)
    return redirect(github_auth_url)

@app.route("/installations")
async def test():
    # TicketEventHandler().bot_comments()

    return await TicketEventHandler().bot_comments()


#Callback url for Github App
@app.route("/register/<discord_userdata>")
async def register(discord_userdata):

    discord_id = discord_userdata

    #Check if the user is registered
    supabase_client = SupabaseInterface()
        
    user_data =  await get_github_data(request.args.get("code"), discord_id=discord_id)

    if supabase_client.contributor_exists(discord_id=discord_id):
        supabase_client.update_contributor(discord_id, user_data)

    #adding to the database
    else:
        supabase_client.add_contributor(user_data)
    
    return await render_template('success.html'), {"Refresh": f'1; url=https://discord.com/channels/{os.getenv("DISCORD_SERVER_ID")}'}



@app.route("/github/events", methods = ['POST'])
async def event_handler():
    supabase_client = SupabaseInterface()
    data = await request.json
    supabase_client.add_event_data(data=data)
    # data = test_data
    if data.get("issue"):
        issue = data["issue"]
        if supabase_client.checkUnlisted(issue["id"]):
            supabase_client.deleteUnlistedTicket(issue["id"])
        await TicketEventHandler().onTicketCreate(data)
        recordIssue(issue)
        if supabase_client.checkIsTicket(issue["id"]):
            
            await TicketEventHandler().onTicketEdit(data)
            if data["action"] == "closed":
                await TicketEventHandler().onTicketClose(data)
    if data.get("installation") and data["installation"].get("account"):
        # if data["action"] not in ["deleted", "suspend"]:
        await TicketEventHandler().updateInstallation(data.get("installation"))

    return data




@app.route("/metrics/discord", methods = ['POST'])
async def discord_metrics():
    request_data = json.loads(await request.json)
    # print(request_data, type(request_data))
    discord_data = []
    last_measured = request_data["measured_at"]
    metrics = request_data["metrics"]
    for product_name, value in metrics.items():
        data = {
            "product_name" : product_name,
            "mentor_messages" : value['mentor_messages'],
            "contributor_messages": value['contributor_messages']     
        }
        discord_data.append(data)

    supabase_client = SupabaseInterface()
    data = supabase_client.add_discord_metrics(discord_data)
    return data.data

@app.route("/metrics/github", methods = ['POST'])
async def github_metrics():
    request_data = json.loads(request.json)
    metrics = request_data["metrics"]
    github_data = []
    for product_name, value in metrics.items():
        data = {
            "product_name" : product_name,
            "open_prs" : value['open_prs'],
            "closed_prs": value['closed_prs'],
            "open_issues": value['open_issues'],
            "closed_issues": value['closed_issues'],
            "number_of_commits": value['number_of_commits'],           
        }
        github_data.append(data)

    supabase_client = SupabaseInterface()
    data = supabase_client.add_github_metrics(github_data)
    return data.data


    
    
# test_data = {
#   "action": "opened",
#   "issue": {
#     "url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/issues/13",
#     "repository_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app",
#     "labels_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/issues/13/labels{/name}",
#     "comments_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/issues/13/comments",
#     "events_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/issues/13/events",
#     "html_url": "https://github.com/KDwevedi/testing_for_github_app/issues/13",
#     "id": 1758000158,
#     "node_id": "I_kwDOJvNYv85oyPQe",
#     "number": 13,
#     "title": "Test 30",
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
#     "created_at": "2023-06-15T04:11:22Z",
#     "updated_at": "2023-06-15T04:11:22Z",
#     "closed_at": None,
#     "author_association": "OWNER",
#     "active_lock_reason": None,
#     "body": "## Description\r\n[Provide a brief description of the feature, including why it is needed and what it will accomplish. You can skip any of Goals, Expected Outcome, Implementation Details, Mockups / Wireframes if they are irrelevant]\r\n\r\n## Goals\r\n- [ ] [Goal 1]\r\n- [ ] [Goal 2]\r\n- [ ] [Goal 3]\r\n- [ ] [Goal 4]\r\n- [ ] [Goal 5]\r\n\r\n## Expected Outcome\r\n[Describe in detail what the final product or result should look like and how it should behave.]\r\n\r\n## Acceptance Criteria\r\n- [ ] [Criteria 1]\r\n- [ ] [Criteria 2]\r\n- [ ] [Criteria 3]\r\n- [ ] [Criteria 4]\r\n- [ ] [Criteria 5]\r\n\r\n## Implementation Details\r\n[List any technical details about the proposed implementation, including any specific technologies that will be used.]\r\n\r\n## Mockups / Wireframes\r\n[Include links to any visual aids, mockups, wireframes, or diagrams that help illustrate what the final product should look like. This is not always necessary, but can be very helpful in many cases.]\r\n\r\n---\r\n\r\n### Project\r\n[Project Name]\r\n\r\n### Organization Name:\r\n[Organization Name]\r\n\r\n### Domain\r\n[Area of governance]\r\n\r\n### Te\r\n[Required technical skills for the project]\r\n\r\n### Mentor(s)\r\n[@Mentor1] [@Mentor2] [@Mentor3]\r\n\r\n### Complexity\r\nPick one of [High]/[Medium]/[Low]\r\n\r\n### Category\r\nPick one or more of [CI/CD], [Integrations], [Performance Improvement], [Security], [UI/UX/Design], [Bug], [Feature], [Documentation], [Deployment], [Test], [PoC]\r\n\r\n### Sub Category\r\nPick one or more of [API], [Database], [Analytics], [Refactoring], [Data Science], [Machine Learning], [Accessibility], [Internationalization], [Localization], [Frontend], [Backend], [Mobile], [SEO], [Configuration], [Deprecation], [Breaking Change], [Maintenance], [Support], [Question], [Technical Debt], [Beginner friendly], [Research], [Reproducible], [Needs Reproduction].\r\n",
#     "reactions": {
#       "url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/issues/13/reactions",
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
#     "timeline_url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/issues/13/timeline",
#     "performed_via_github_app": None,
#     "state_reason": None
#   },
#   "label": {
#     "id": 5618368045,
#     "node_id": "LA_kwDOJvNYv88AAAABTuF-LQ",
#     "url": "https://api.github.com/repos/KDwevedi/testing_for_github_app/labels/C4GT%20Community",
#     "name": "C4GT Community",
#     "color": "3C6698",
#     "default": False,
#     "description": "C4GT Community Ticket"
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
#     "updated_at": "2023-06-15T04:08:05Z",
#     "pushed_at": "2023-06-14T06:43:14Z",
#     "git_url": "git://github.com/KDwevedi/testing_for_github_app.git",
#     "ssh_url": "git@github.com:KDwevedi/testing_for_github_app.git",
#     "clone_url": "https://github.com/KDwevedi/testing_for_github_app.git",
#     "svn_url": "https://github.com/KDwevedi/testing_for_github_app",
#     "homepage": None,
#     "size": 4,
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
#     "open_issues_count": 13,
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
#     "open_issues": 13,
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

# event_handler()