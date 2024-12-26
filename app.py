from quart import Quart, redirect, render_template, request, jsonify, current_app
from werkzeug.exceptions import BadRequestKeyError
from io import BytesIO
import aiohttp, asyncio
import dotenv, os, json, urllib, sys, dateutil, datetime, sys
from utils.github_adapter import GithubAdapter
from utils.dispatcher import dispatch_event
from utils.link_pr_issue import AddIssueId
from utils.webhook_auth import verify_github_webhook
from utils.db import SupabaseInterface,PostgresORM
from events.ticketEventHandler import TicketEventHandler
from events.ticketFeedbackHandler import TicketFeedbackHandler
from githubdatapipeline.pull_request.scraper import getNewPRs
from githubdatapipeline.pull_request.processor import PrProcessor
from githubdatapipeline.issues.destination import recordIssue
from supabasedatapipeline.github_profile_render.ingestor import GithubProfileDisplay
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from quart_trio import QuartTrio  # Required for Quart with APScheduler
import httpx
from utils.logging_file import logger
from utils.connect_db import connect_db
from utils.helpers import *
from datetime import datetime
from quart_cors import cors
from utils.migrate_tickets import MigrateTickets
from utils.migrate_users import MigrateContributors

scheduler = AsyncIOScheduler()

fpath = os.path.join(os.path.dirname(__file__), 'utils')
sys.path.append(fpath)

dotenv.load_dotenv(".env")

app = Quart(__name__)
# Enable CORS on all routes
app = cors(app, allow_origin="*")
app.config['TESTING']= False




async def get_github_data(code, discord_id):

    async with aiohttp.ClientSession() as session:
        github_response = await GithubAdapter.get_github_data(code)
        auth_token = (github_response)["access_token"]
       
        headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {auth_token}"
        }

        user_response = await GithubAdapter.get_github_user(headers)
        user = user_response
        github_id = user["id"]
        github_username = user["login"]

        # Fetching user's private emails
        if "user:email" in github_response["scope"]:
            # print("🛠️GETTING USER EMAIL", locals(), file=sys.stderr)
            async with session.get("https://api.github.com/user/emails", headers=headers) as email_response:
                emails = await email_response.json()
                private_emails = [email["email"] for email in emails if email["verified"]]
        else:
            private_emails = []

        user_data = {
            "discord_id": int(discord_id),
            "github_id": github_id,
            "github_url": f"https://github.com/{github_username}",
            "email": ','.join(private_emails),
            "joined_at": datetime.now()
        }

        return user_data
            
async def comment_cleaner():
    while True:
        await asyncio.sleep(5)
        comments = await PostgresORM().readAll("app_comments")
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
                print(await PostgresORM().deleteComment(issue_id,"app_comments"))

async def fetch_github_issues_from_repo(owner, repo):
    try:
        response = await GithubAdapter.fetch_github_issues_from_repo(owner,repo)
        if response:
            return response
        else:
            print(f"Failed to get issues: {response}")
                
    except Exception as e:
        logger.info(e)
        raise Exception
    
repositories_list = [
    "KDwevedi/c4gt-docs",
    "KDwevedi/testing_for_github_app"
    # Add more repositories as needed
]
productList = [
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
@app.route("/")
async def hello_world():
    return "hello world"

@app.route("/verify/<githubUsername>")
async def verify(githubUsername):
    return await render_template('verified.html')


@app.route("/misc_actions")
async def addIssues():
    tickets = await PostgresORM().readAll("ccbp_tickets")
    count =1
    for ticket in tickets:
        print(f'{count}/{len(tickets)}')
        count+=1
        if ticket["status"] == "closed":
            # if ticket["api_endpoint_url"] in ["https://api.github.com/repos/glific/glific/issues/2824"]:
            await TicketEventHandler().onTicketClose({"issue":await get_url(ticket["api_endpoint_url"])})
    

    return '' 


@app.route("/update_profile", methods=["POST"])
async def updateGithubStats():
    webhook_data = await request.json
    data = await PostgresORM().read("github_profile_data", filters={"dpg_points": ("gt", 0)})
    GithubProfileDisplay().update(data)
    return 'Done'

@app.before_serving
async def startup():
    app.add_background_task(do_update)
async def do_update():
    while True:
        print("Starting Update")
        await asyncio.sleep(21600)
        data = await PostgresORM().read("github_profile_data", filters={"dpg_points": ("gt", 0)})
        GithubProfileDisplay().update(data)


@app.route("/already_authenticated")
async def isAuthenticated():
    print(f'already authenticated at {datetime.now()}')
    return await render_template('success.html'), {"Refresh": f'2; url=https://discord.com/channels/{os.getenv("DISCORD_SERVER_ID")}'}

@app.route("/authenticate/<discord_userdata>")
async def authenticate(discord_userdata):
    print("🛠️STARTING AUTHENTICATION FLOW", locals(), file=sys.stderr)
    redirect_uri = f'{os.getenv("HOST")}/register/{discord_userdata}'
    # print(redirect_uri)
    github_auth_url = f'https://github.com/login/oauth/authorize?client_id={os.getenv("GITHUB_CLIENT_ID")}&redirect_uri={redirect_uri}&scope=user:email'
    print(github_auth_url, file=sys.stderr)
    print("🛠️REDIRECTION TO GITHUB", locals(), file=sys.stderr)
    return redirect(github_auth_url)

@app.route("/installations")
async def test():
    # TicketEventHandler().bot_comments()

    return await TicketEventHandler().bot_comments()


#Callback url for Github App
@app.route("/register/<discord_userdata>")
async def register(discord_userdata):
    print("🛠️SUCCESSFULLY REDIECTED FROM GITHUB TO SERVER", locals(), file=sys.stderr)
    postgres_client = PostgresORM()

    discord_id = discord_userdata
    print("🛠️SUCCESFULLY DEFINED FUNCTION TO POST TO SUPABASE", locals(), file=sys.stderr)
    # supabase_client = SupabaseInterface.get_instance()
    print("🛠️GETTING AUTH CODE FROM GITHUB OAUTH FLOW", locals(), file=sys.stderr)
    if not request.args.get("code"):
        raise BadRequestKeyError()
    user_data = await get_github_data(request.args.get("code"), discord_id=discord_id)
    # print("🛠️OBTAINED USER DATA", locals(), file=sys.stderr)
    # data = supabase_client.client.table("contributors").select("*").execute()
    try:
        # resp = await post_to_supabase(user_data)
        resp = await postgres_client.add_data(user_data, "contributors_registration")
        print("🛠️PUSHED USER DETAILS TO SUPABASE")
    except Exception as e:
        print("🛠️ENCOUNTERED EXCEPTION PUSHING TO SUPABASE",e, file=sys.stderr)
    
    print("🛠️FLOW COMPLETED SUCCESSFULLY, REDIRECTING TO DISCORD", file=sys.stderr)
    return await render_template('success.html'), {"Refresh": f'1; url=https://discord.com/channels/{os.getenv("DISCORD_SERVER_ID")}'}


@app.route("/github/events", methods = ['POST'])
async def event_handler():
    try:
        data = await request.json
        print('data is ', data)
        secret_key = os.getenv("WEBHOOK_SECRET") 

        verification_result, error_message = await verify_github_webhook(request,secret_key)
            
        postgres_client = PostgresORM.get_instance()
        event_type = request.headers.get("X-GitHub-Event")
        await dispatch_event(event_type, data, postgres_client)
            
        return data
    except Exception as e:
        logger.info(e)
        return "Server Error"


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

    data = await PostgresORM().add_discord_metrics(discord_data)
    return data

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

    data =  await PostgresORM().add_github_metrics(github_data)
    return data

@app.route("/role-master")
async def get_role_master():
    role_masters = await PostgresORM().readAll("role_master")
    print('role master ', role_masters)
    return role_masters.data

@app.route("/program-tickets-user", methods = ['POST'])
async def get_program_tickets_user():
    try:
        print('getting data for users leader board')
        request_data = request.body._data
        filter = ''
        if request_data:
            filter = json.loads(request_data.decode('utf-8'))
        postgres_client = PostgresORM.get_instance()
        all_issues = await postgres_client.fetch_filtered_issues(filter)
        print('length of all issue ', len(all_issues))

        issue_result = []
        for issue in all_issues:
            reqd_skills = []
            project_type = []

            # Process 'reqd_skills'
            if issue["issue"]["technology"]:
                reqd_skills = [skill.strip().replace('"', '') for skill in issue["issue"]["technology"].split(',')]

            # Process 'project_type'
            if issue["issue"]["project_type"]:
                project_type = [ptype.strip().replace('"', '') for ptype in issue["issue"]["project_type"].split(',')]

            #labels are extracted and in case the label is C4GT Community then it is replaced by C4GT Coding
            labels = issue["issue"]["labels"]
            if len(labels) == 1:
                labels = ['C4GT Coding']
            else:
                labels = [label for label in labels if label != 'C4GT Community']

            contributors_data = issue["contributors_registration"]
            if contributors_data:
                contributors_name = contributors_data["name"] 
                if contributors_name:
                    pass
                else: 
                    contributors_url = contributors_data["github_url"].split('/')
                    contributors_name = contributors_url[-1] if contributors_url else None

            res = {
                "created_at": issue["issue"]["created_at"] if issue["issue"]["created_at"] else None,
                "name": issue["issue"]["title"],
                "complexity": issue["issue"]["complexity"],
                "category": labels,
                "reqd_skills": reqd_skills if reqd_skills else None,
                "issue_id": issue["issue"]["issue_id"],
                "url": issue["issue"]["link"],
                "ticket_points": issue["points"]["points"] if issue["points"] else None,
                "mentors": [
                    "Amoghavarsh"
                ],
                "status": issue["issue"]["status"],
                "domain": issue["issue"]["domain"],
                "organization": issue["org"]["name"],
                "closed_at": "2024-08-06T06:59:10+00:00",
                "assignees": contributors_name if contributors_data else None,
                "project_type": project_type if reqd_skills else None,
                "is_assigned": True if contributors_data else False
            }
            issue_result.append(res)

        return issue_result
    except Exception as e:
        print('Exception occured in getting users leaderboard data ', e)
        return 'failed'

@app.route('/migrate-tickets')
async def migrate_tickets():
    try:
        migrator = MigrateTickets()  # Create an instance
        return await migrator.migrate_ccbp_tickets()
    except Exception as e:
        print('exception occured ', e)
        return 'failed'
    

@app.route('/migrate-contributors')
async def migrate_contributors():
    try:
        migrator = MigrateContributors()  # Create an instance

        asyncio.create_task(migrator.migration())
        return 'migration started'
    except Exception as e:
        print('exception occured ', e)
        return 'failed'


@app.route('/add-issue-id-pr')
async def add_issue_id_pr():
    try:
        migrator = AddIssueId()  # Create an instance

        asyncio.create_task(migrator.process_prs())
        
        # return await migrator.process_prs()
        return 'migration started'
    except Exception as e:
        print('exception occured ', e)
        return 'failed'
    

if __name__ == '__main__':
    app.run()