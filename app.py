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
    if request.method == "POST":
        product = request.form.get("product")
        if product:
            productList.append(product)
    return await render_template('form.html',repositories=repositories_list,  products=productList)

@app.route("/submission", methods = ['POST'])
async def formResponse():
    response = await request.form
    data = response.to_dict()
    print(data)
    email_data = {
        "organisation": "KDwevedi",
        "email": data["email"],
        "repos": [{"name":f'{key[18:]}', "product":f'{value}'} for key,value in data.items() if 'product-selection-' in key],
        "auth_link": "www.dummylink.com"
    }
    data = {
        "organisation": "KDwevedi",
        "email": data["email"],
        "repos": [{"name":f'{key[18:]}', "product":f'{value}'} for key,value in data.items() if 'product-selection-' in key]
    }
    NewRegistration().createNewReg(email_data)
    SupabaseInterface().insert("Onboarding_Dev",data)
    return data

@app.route("/form/edit/<organisation>")
async def editForm(organisation):
    reges = SupabaseInterface().readAll("Onboarding_Dev")
    for reg in reges:
        if reg["organisation"]== organisation:
            mapping = dict()
            data = reg["repos"]
            for repo in data:
                mapping[repo["name"]] = repo["product"]
            print(mapping)
            return await render_template('editableForm.html',repositories=repositories_list,  products=productList, email = reg["email"], product_selections=mapping)
    return 'Installation not found'


@app.route("/success")
async def successResponse():
    return await render_template('formAknowledgement.html')

@app.route("/misc_actions")
async def addIssues():
    tickets = SupabaseInterface().readAll("ccbp_tickets")
    count =1
    for ticket in tickets:
        print(f'{count}/{len(tickets)}')
        count+=1
        if ticket["status"] == "closed":
            # if ticket["api_endpoint_url"] in ["https://api.github.com/repos/glific/glific/issues/2824"]:
            await TicketEventHandler().onTicketClose({"issue":await get_url(ticket["api_endpoint_url"])})
    

    # prs = SupabaseInterface().readAll("mentorship_program_pull_request")
    # tickets = SupabaseInterface().readAll("mentorship_program_tickets")
    # ticketUrls = [ticket["html_url"] for ticket in tickets]
    # for pr in prs:
    #     if pr.get("body"):
    #         issues = PrProcessor().getLinkedIssues(pr)
    #         for issue in issues:
    #             if pr["repository_url"]+f'/issues/{issue}' in ticketUrls:
    #                 SupabaseInterface().update("mentorship_program_pull_request", {"linked_ticket":pr["repository_url"]+f'/issues/{issue}' }, "pr_id", pr["pr_id"])
    # return "Hello World"

    # await recordIssue({})
    return '' 
        

    # await getNewPRs()
    # return ""

@app.route("/update_profile", methods=["POST"])
async def updateGithubStats():
    webhook_data = await request.json
    GithubProfileDisplay().update(webhook_data)
    return webhook_data

@app.route("/github_profile/<discord_id>", methods = ["GET"])
async def renderActivitySummary(discord_id):
    return discord_id


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
    if data.get("issue"):
        issue = data["issue"]
        recordIssue(issue)
        if supabase_client.checkUnlisted(issue["id"]):
            supabase_client.deleteUnlistedTicket(issue["id"])
        await TicketEventHandler().onTicketCreate(data)
        if supabase_client.checkIsTicket(issue["id"]):
            await TicketEventHandler().onTicketEdit(data)
            if data["action"] == "closed":
                await TicketEventHandler().onTicketClose(data)
    if data.get("installation") and data["installation"].get("account"):
        # if data["action"] not in ["deleted", "suspend"]:
        await TicketEventHandler().updateInstallation(data.get("installation"))
    
    # if data.

    return data

@app.route("/image", methods=["GET"])
async def get_image():
    # client = minio.Minio(f"{os.getenv('MINIO_HOST')}:{os.getenv('MINIO_PORT')}", f"{os.getenv('MINIO_ACCESS_KEY')}","m4UcAe3d1omV", secure=False)
    # bucket = "c4gt-github-profiles"
    # file = "RisingStar.png"

    # with client.get_object(bucket, file, request_headers= {
    #     "Content-Type": "image/png"
    # }) as f:
    #     image = await f.read()

    res = SupabaseInterface().client.storage.from_("c4gt-github-profile").get_public_url('RisingStar.png')


    return res



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