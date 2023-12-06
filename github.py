import os, sys, dotenv

# Get the absolute path of the root directory (parent of the current script's directory)
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the utils directory to sys.path
utils_path = os.path.join(root_dir, 'utils')
sys.path.append(utils_path)

dotenv.load_dotenv(".env")

from utils.github_api import GithubAPI
from utils.jwt_generator import GenerateJWT
from utils.db import SupabaseInterface
import aiohttp, asyncio


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

async def saveInstallations():
    installations = await get_installations()
    for installation in installations:
        SupabaseInterface().recordInstallation(installation)


print(asyncio.run(saveInstallations()))