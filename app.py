from quart import Quart, redirect, render_template, request, jsonify, current_app
from werkzeug.exceptions import BadRequestKeyError
from io import BytesIO
import aiohttp, asyncio
import dotenv, os, json, urllib, sys, dateutil, datetime, sys
from utils.github_adapter import GithubAdapter
from utils.dispatcher import dispatch_event
from utils.webhook_auth import verify_github_webhook
from utils.db import SupabaseInterface
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

scheduler = AsyncIOScheduler()

fpath = os.path.join(os.path.dirname(__file__), 'utils')
sys.path.append(fpath)

dotenv.load_dotenv(".env")

app = Quart(__name__)
app.config['TESTING']= False


async def get_github_data(code, discord_id):
   
    headers = {
        "Accept": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        r = await GithubAdapter.get_github_data(code)

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
        comments = SupabaseInterface.get_instance().readAll("app_comments")
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
                print(SupabaseInterface.get_instance().deleteComment(issue_id))

async def fetch_github_issues_from_repo(owner, repo):
    try:
        response = await GithubAdapter.fetch_github_issues_from_repo(owner,repo)
        if response:
            return response
        else:
            print(f"Failed to get issues: {response}")
                
    except Exception as e:
        logger.info(e)
        pass
    
          
                
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
    tickets = SupabaseInterface.get_instance().readAll("ccbp_tickets")
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
    data = SupabaseInterface.get_instance().read("github_profile_data", filters={"dpg_points": ("gt", 0)})
    GithubProfileDisplay().update(data)
    return 'Done'

@app.before_serving
async def startup():
    app.add_background_task(do_update)
async def do_update():
    while True:
        print("Starting Update")
        await asyncio.sleep(21600)
        data = SupabaseInterface.get_instance().read("github_profile_data", filters={"dpg_points": ("gt", 0)})
        GithubProfileDisplay().update(data)


@app.route("/already_authenticated")
async def isAuthenticated():
    return await render_template('success.html'), {"Refresh": f'2; url=https://discord.com/channels/{os.getenv("DISCORD_SERVER_ID")}'}

@app.route("/authenticate/<discord_userdata>")
async def authenticate(discord_userdata):

    redirect_uri = f'{os.getenv("HOST")}/register/{discord_userdata}'
    # print(redirect_uri)
    github_auth_url = f'https://github.com/login/oauth/authorize?client_id={os.getenv("GITHUB_CLIENT_ID")}&redirect_uri={redirect_uri}&scope=user:email'
    print(github_auth_url, file=sys.stderr)
    return redirect(github_auth_url)

@app.route("/installations")
async def test():
    # TicketEventHandler().bot_comments()

    return await TicketEventHandler().bot_comments()


#Callback url for Github App
@app.route("/register/<discord_userdata>")
async def register(discord_userdata):
    SUPABASE_URL = 'https://kcavhjwafgtoqkqbbqrd.supabase.co/rest/v1/contributors_registration'
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Ensure this key is kept secure.

    async def post_to_supabase(json_data):
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal',
        }

        # As aiohttp recommends, create a session per application, rather than per function.
        async with aiohttp.ClientSession() as session:
            async with session.post(SUPABASE_URL, json=json_data, headers=headers) as response:
                status = response.status
                # Depending on your requirements, you may want to process the response here.
                response_text = await response.text()

                if status != 201:
                    raise Exception(response_text)

        return status, response_text
    discord_id = discord_userdata

    supabase_client = SupabaseInterface.get_instance()
    if not request.args.get("code"):
        raise BadRequestKeyError()
    user_data = await get_github_data(request.args.get("code"), discord_id=discord_id)
    print(user_data, file=sys.stderr)

    # data = supabase_client.client.table("contributors").select("*").execute()
    try:
        resp = await post_to_supabase(user_data)
        print(resp)
    except Exception as e:
        print(e)
    
    return await render_template('success.html'), {"Refresh": f'1; url=https://discord.com/channels/{os.getenv("DISCORD_SERVER_ID")}'}


@app.route("/github/events", methods = ['POST'])
async def event_handler():
    try:
        data = await request.json
        secret_key = os.getenv("WEBHOOK_SECRET") 

        verification_result, error_message = await verify_github_webhook(request,secret_key)
        if not verification_result:
            return "Webhook verification failed.", 403
            
        supabase_client = SupabaseInterface.get_instance()
        event_type = request.headers.get("X-GitHub-Event")
        await dispatch_event(event_type, data, supabase_client)
            
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

    supabase_client = SupabaseInterface.get_instance()
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

    supabase_client = SupabaseInterface.get_instance()
    data = supabase_client.add_github_metrics(github_data)
    return data.data

@app.route('/job_classroom')
async def my_scheduled_job_test():
    # Define the GitHub API endpoint URL
    assignment_id = os.getenv("ASSIGNMENT_ID") 
    page = 1
    while True:
        try:
            # Make the request to the GitHub API
            response,code = await GithubAdapter.get_calssroom_data(assignment_id,page)
            # Check if the request was successful
            if code == 200:
                # Return the response from the GitHub API
                if response == [] or len(response)==0:
                    break
                conn, cur = connect_db()    
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
                    val['updated_at'] = datetime.datetime.now()
                    try:
                        git_url = "https://github.com/"+val['github_username']

                    except:
                        git_url = val['students'][0]['html_url'] 

                                
                    sql_query = getdiscord_from_cr()
                    cur.execute(sql_query, (git_url,))                    
                    discord_id = cur.fetchone()
                    val['discord_id'] = discord_id[0] if discord_id else None

                    if val['discord_id']:
                        # Execute the SQL query
                        cur.execute(check_assignment_exist(),(str(val['discord_id']),str(assignment_id)))
                        exist_assignment = cur.fetchone()[0]

                        if exist_assignment:
                            update_data.append(val)
                        else:
                            create_data.append(val)
                    res.append(val)
                create_rec = save_classroom_records(create_data)
                update_rec = update_classroom_records(update_data)
                # Close cursor and connection
                cur.close()
                conn.close()
                logger.info(f"{datetime.datetime.now()}---jobs works")

                # return res
            else:
                # Return an error message if the request failed
                return {'error': f'Failed to fetch data from GitHub API: {response.status_code}'}, response.status_code
        except httpx.HTTPError as e:
            logger.info(e)
            # Return an error message if an HTTP error occurred
            return {'error': f'HTTP error occurred: {e}'}, 500
            
        page = page + 1

# #CRON JOB
@app.before_serving
async def start_scheduler():
    scheduler.add_job(my_scheduled_job_test, 'interval', hours=1)
    scheduler.start()


if __name__ == '__main__':
    app.run()