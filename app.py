from quart import Quart, redirect, render_template, request, jsonify, current_app
from werkzeug.exceptions import BadRequestKeyError
from io import BytesIO
import aiohttp, asyncio
import dotenv, os, json, urllib, sys, dateutil, datetime, sys
from utils.github_adapter import GithubAdapter
from utils.dispatcher import dispatch_event
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

scheduler = AsyncIOScheduler()

fpath = os.path.join(os.path.dirname(__file__), 'utils')
sys.path.append(fpath)

dotenv.load_dotenv(".env")

app = Quart(__name__)
# Enable CORS on all routes
app = cors(app, allow_origin="*")
app.config['TESTING']= False




async def get_github_data(code, discord_id):
   
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {auth_token}"

    }

    async with aiohttp.ClientSession() as session:
        github_resposne = await GithubAdapter.get_github_data(code)
        auth_token = (github_resposne)["access_token"]
       
        user_response = await GithubAdapter.get_github_user(headers)
        user = user_response
        github_id = user["id"]
        github_username = user["login"]

        # Fetching user's private emails
        if "user:email" in github_resposne["scope"]:
            print("🛠️GETTING USER EMAIL", locals(), file=sys.stderr)
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
    
          
                
# @app.before_serving
# async def startup():
#     app.add_background_task(comment_cleaner)
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
    # if request.method == "POST":
    #     product = request.form.get("product")
    #     if product:
    #         productList.append(product)
    # return await render_template('form.html',repositories=repositories_list,  products=productList)
    return "hello world"

@app.route("/verify/<githubUsername>")
async def verify(githubUsername):
    return await render_template('verified.html')

# @app.route("/submission", methods = ['POST'])
# async def formResponse():
#     response = await request.form
#     data = response.to_dict()
#     print(data)
#     email_data = {
#         "organisation": "KDwevedi",
#         "email": data["email"],
#         "repos": [{"name":f'{key[18:]}', "product":f'{value}'} for key,value in data.items() if 'product-selection-' in key],
#         "auth_link": "www.dummylink.com"
#     }
#     data = {
#         "organisation": "KDwevedi",
#         "email": data["email"],
#         "repos": [{"name":f'{key[18:]}', "product":f'{value}'} for key,value in data.items() if 'product-selection-' in key]
#     }
#     NewRegistration().createNewReg(email_data)
#     SupabaseInterface().insert("Onboarding_Dev",data)
#     return data

# @app.route("/form/edit/<organisation>")
# async def editForm(organisation):
#     reges = SupabaseInterface().readAll("Onboarding_Dev")
#     for reg in reges:
#         if reg["organisation"]== organisation:
#             mapping = dict()
#             data = reg["repos"]
#             for repo in data:
#                 mapping[repo["name"]] = repo["product"]
#             print(mapping)
#             return await render_template('editableForm.html',repositories=repositories_list,  products=productList, email = reg["email"], product_selections=mapping)
#     return 'Installation not found'


# @app.route("/success")
# async def successResponse():
#     return await render_template('formAknowledgement.html')

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


# @app.route("/image", methods=["GET"])
# async def serve_image():
#     try:
#         # Fetch the image from the Supabase bucket
#         res = SupabaseInterface().client.storage.from_("c4gt-github-profile").download("RisingStar.png")

#         # Convert the content to a BytesIO object and serve it
#         return Response(res, mimetype="image/jpeg")

#     except Exception as e:
#         print(f"Error: {e}")
#         abort(500)

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

    # async def post_to_supabase(json_data):
    #     # As aiohttp recommends, create a session per application, rather than per function.
    #     async with aiohttp.ClientSession() as session:
    #         async with session.put(SUPABASE_URL, json=json_data, headers=headers) as response:
    #             status = response.status
    #             # Depending on your requirements, you may want to process the response here.
    #             response_text = await response.text()

    #             if status != 201:
    #                 raise Exception(response_text)

    #     return status, response_text
    discord_id = discord_userdata
    print("🛠️SUCCESFULLY DEFINED FUNCTION TO POST TO SUPABASE", locals(), file=sys.stderr)
    # supabase_client = SupabaseInterface.get_instance()
    print("🛠️GETTING AUTH CODE FROM GITHUB OAUTH FLOW", locals(), file=sys.stderr)
    if not request.args.get("code"):
        raise BadRequestKeyError()
    user_data = await get_github_data(request.args.get("code"), discord_id=discord_id)
    print("🛠️OBTAINED USER DATA", locals(), file=sys.stderr)
    # data = supabase_client.client.table("contributors").select("*").execute()
    try:
        # resp = await post_to_supabase(user_data)
        resp = await postgres_client.add_data(user_data, "contributors_registration")
        print("🛠️PUSHED USER DETAILS TO SUPABASE", resp, file=sys.stderr)
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
        # if not verification_result:
        #     return "Webhook verification failed.", 403
            
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

@app.route('/job_classroom')
async def my_scheduled_job_test():
    # Define the GitHub API endpoint URL
    assignment_id = os.getenv("ASSIGNMENT_ID") 
    page = 1
    while True:
        try:
            # Make the request to the GitHub API
            response,code = await GithubAdapter.get_classroom_data(assignment_id,page)
            # Check if the request was successful
            if code == 200:
                # Return the response from the GitHub API
                if response == [] or len(response)==0:
                    break
                # conn, cur = connect_db()    
                res =[]
                create_data = []
                update_data = []
                for val in response:
                    if val['grade']:
                        parts = val['grade'].split("/")
                        # Convert each part into integers
                        val['points_awarded'] = int(parts[0])
                        val['points_available'] = int(parts[1])

                    else:
                        val['points_awarded'] = 0
                        val['points_available'] = 0

                    percent = (float(val['points_awarded'])/float(val['points_available'])) * 100 if val['grade'] else 0
                    val['c4gt_points']= calculate_points(percent)
                    if val['c4gt_points'] > 100:
                        logger.info(f"OBJECT DISCORDED DUE TO MAX POINT LIMIT --- {val['github_username']} -- {assignment_id}")
                        continue

                    val['assignment_id'] = assignment_id
                    val['updated_at'] = datetime.now()
                    try:
                        git_url = "https://github.com/"+val['github_username']

                    except:
                        git_url = val['students'][0]['html_url'] 
                    
                    discord_id = await PostgresORM().getdiscord_from_cr(git_url)
                    val['discord_id'] = discord_id if discord_id else None

                    if val['discord_id']:
                        exist_assignment = await PostgresORM().check_exists(str(val['discord_id']),str(assignment_id))

                        if exist_assignment:
                            update_data.append(val)
                        else:
                            create_data.append(val)
                    res.append(val)
                create_rec = await PostgresORM().save_classroom_records(create_data)
                update_rec = await PostgresORM().update_classroom_records(update_data)
              
                logger.info(f"{datetime.now()}---jobs works")

                # return res
            else:
                return {'error': f'Failed to fetch data from GitHub API: {response.status_code}'}, response.status_code
        except httpx.HTTPError as e:
            logger.info(e)
            # Return an error message if an HTTP error occurred
            return {'error': f'HTTP error occurred: {e}'}, 500
            
        page = page + 1

@app.route("/role-master")
async def get_role_master():
    # x = SupabaseInterface().get_instance()
    # role_masters = x.client.table(f"role_master").select("*").execute()
    role_masters = await PostgresORM().readAll("role_master")
    print('role master ', role_masters)
    return role_masters.data


@app.route("/leaderboard-user", methods = ['POST'])
async def get_leaderboard_user():
    try:
        print('getting data for users leader board')
        request_data = request.body._data
        filter = ''
        if request_data:
            filter = json.loads(request_data.decode('utf-8'))
        postgres_client = PostgresORM.get_instance()
        # issues and contributors and mentors and their points
        # all_issues = await postgres_client.getUserLeaderBoardData()
        all_issues = await postgres_client.fetch_filtered_issues(filter)
        print('issues are ', all_issues)
        issue_result = []
        for issue in all_issues:
            res = {
                "created_at": "2023-11-24T11:36:22.965699+00:00",
                "name": issue["issue"]["title"],
                "complexity": issue["issue"]["complexity"],
                "category": issue["issue"]["labels"],
                "reqd_skills": issue["issue"]["technology"].split(','),
                "issue_id": issue["issue"]["issue_id"],
                "api_endpoint_url": "https://api.github.com/repos/ELEVATE-Project/frontend-utils-library/issues/3",
                "url": issue["issue"]["link"],
                "ticket_points": issue["points"]["points"] if issue["points"] else None,
                "index": 245,
                "mentors": [
                    "Amoghavarsh"
                ],
                "uuid": "63334ef2-457c-462a-9127-c4a339cdf5f4", #what's the need here
                "status": issue["issue"]["status"],
                "community_label": False,
                "organization": issue["org"]["name"],
                "closed_at": "2024-08-06T06:59:10+00:00",
                "assignees": None,
                "issue_author": [
                    "kiranharidas187"
                ],
                "is_assigned": False
            }
            issue_result.append(res)

        return issue_result
    except Exception as e:
        print('Exception occured in getting users leaderboard data ', e)
        return 'failed'

# #CRON JOB
# @app.before_serving
# async def start_scheduler():
#     scheduler.add_job(my_scheduled_job_test, 'interval', hours=1)
#     scheduler.start()


if __name__ == '__main__':
    app.run()