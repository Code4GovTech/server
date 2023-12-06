from quart import Blueprint, render_template, redirect, request
import aiohttp
import os, sys

from ..config import DiscordConfig
from utils.db import SupabaseInterface

discordConfig = DiscordConfig()
contributor = Blueprint('contributor', __name__, template_folder='templates')

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


@contributor.route('/', methods=["GET"])
async def isLive():
    return "/contributor endpoints"

@contributor.route("/authenticated")
async def isAuthenticated():
    return await render_template('success.html'), {"Refresh": f'2; url=https://discord.com/channels/{discordConfig.SERVER_ID}/{discordConfig.INTRODUCTION_CHANNEL}'}

@contributor.route("/authenticate/<discord_id>")
async def authenticate(discord_userdata):

    redirect_uri = f'{os.getenv("HOST")}/register/{discord_userdata}'
    # print(redirect_uri)
    github_auth_url = f'https://github.com/login/oauth/authorize?client_id={os.getenv("GITHUB_CLIENT_ID")}&redirect_uri={redirect_uri}&scope=user:email'
    print(github_auth_url, file=sys.stderr)
    return redirect(github_auth_url)

@contributor.route("/register/<discord_userdata>")
async def register(discord_userdata):
    SUPABASE_URL = 'https://kcavhjwafgtoqkqbbqrd.supabase.co/rest/v1'
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    async def post_to_supabase(json_data):
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'resolution=merge-duplicates,return=minimal',
        }

        # Update this URL to point to the specific table and column for upsert
        SUPABASE_TABLE_URL = f"{SUPABASE_URL}/contributors"

        async with aiohttp.ClientSession() as session:
            async with session.post(SUPABASE_TABLE_URL, json=json_data, headers=headers) as response:
                status = response.status
                response_text = await response.text()

        return status, response_text
    
    discord_id = discord_userdata
    user_data = await get_github_data(request.args.get("code"), discord_id=discord_id)

    try:
        await post_to_supabase(user_data)
    except Exception as e:
        print(e)
    
    return await render_template('success.html'), {"Refresh": f'1; url=https://discord.com/channels/{os.getenv("DISCORD_SERVER_ID")}'}
