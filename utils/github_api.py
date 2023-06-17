from utils.jwt_generator import GenerateJWT
import aiohttp
class GithubAPI:
    def __init__(self):
        self.headers = {
            'Accept': 'application/vnd.github+json',
            # 'Authorization': f'Bearer {os.getenv("GithubPAT")}'
        }
        return
    
    def authenticate_app_as_installation(self, repo_owner):
        installation_id = 0
        jwt = GenerateJWT().__call__()
        url = f"https://api.github.com/app/installations"
        self.headers["Authorization"]=f'Bearer {jwt}'
        installations = []#requests.get(url, headers=self.headers).json()
        for installation in installations:
            if installation["account"]["login"] == repo_owner:
                installation_id = installation["id"]
                url=f"https://api.github.com/app/installations/{installation_id}/access_tokens"
        
        if not installation_id:
            return None
        token_req = s#requests.post(url=url, headers=self.headers).json()
        return token_req["token"]

        

