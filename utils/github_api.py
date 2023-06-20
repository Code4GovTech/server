from utils.jwt_generator import GenerateJWT
import aiohttp
class GithubAPI:
    def __init__(self):
        self.headers = {
            'Accept': 'application/vnd.github+json',
            # 'Authorization': f'Bearer {os.getenv("GithubPAT")}'
        }
        return
    
    async def authenticate_app_as_installation(repo_owner):
        installation_id = 0
        jwt = GenerateJWT().__call__()
        url = "https://api.github.com/app/installations"
        headers = {
            "Authorization": f"Bearer {jwt}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                installations = await response.json()

                for installation in installations:
                    if installation["account"]["login"] == repo_owner:
                        installation_id = installation["id"]
                        url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"

                if not installation_id:
                    return None

                async with session.post(url, headers=headers) as token_response:
                    token_req = await token_response.json()
                    return token_req["token"]

        

