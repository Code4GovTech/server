from quart import Quart, request, jsonify
import aiohttp, asyncio
import dotenv, os, json, sys, dateutil, datetime, sys
from utils.db import SupabaseInterface
from events.ticketEventHandler import TicketEventHandler
from events.ticketFeedbackHandler import TicketFeedbackHandler
from supabasedatapipeline.github_profile_render.ingestor import GithubProfileDisplay
from .contributor import contributor
from .github import github

fpath = os.path.join(os.path.dirname(__file__), 'utils')
sys.path.append(fpath)
dotenv.load_dotenv(".env")

app = Quart(__name__)
app.config['TESTING']= True
app.register_blueprint(contributor)
app.register_blueprint(github)


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

async def fetch_github_issues_from_repo(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {os.getenv("GithubPAT")}',
        'X-GitHub-Api-Version': '2022-11-28'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                issues = await response.json()
                return issues
            else:
                print(f"Failed to get issues: {response.status}")
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
    tickets = SupabaseInterface().readAll("ccbp_tickets")
    count =1
    for ticket in tickets:
        print(f'{count}/{len(tickets)}')
        count+=1
        if ticket["status"] == "closed":
            print('')
            # if ticket["api_endpoint_url"] in ["https://api.github.com/repos/glific/glific/issues/2824"]:
            # await TicketEventHandler().onTicketClose({"issue":await get_url(ticket["api_endpoint_url"])})
    

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
    return jsonify(webhook_data)

@app.before_serving
async def startup():
    app.add_background_task(do_update)
async def do_update():
    while True:
        await asyncio.sleep(21600)
        data = SupabaseInterface().read("github_profile_data", filters={"points": ("gt", 0)})
        GithubProfileDisplay().update(data)

@app.route("/installations")
async def test():
    # TicketEventHandler().bot_comments()

    return await TicketEventHandler().bot_comments()


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