import os
from typing import Any
from supabase import create_client, Client
import dotenv

dotenv.load_dotenv(".env")

# url: str = os.getenv("SUPABASE_URL")
# key: str = os.getenv("SUPABASE_KEY")

class SupabaseInterface:
    def __init__(self, url, key) -> None:
        self.supabase_url = url
        self.supabase_key = key
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
    
    def add_mentor(self, userdata):
        
        data = self.client.table("mentors").insert(userdata).execute()
        print(data.data)
        return data
    
    def add_contributor(self, userdata):
        
        data = self.client.table("contributors").insert(userdata).execute()
        print(data.data)
        return data
    
    def mentor_exists(self, discord_id):
        data = self.client.table("mentors").select("*").eq("discord_id", discord_id).execute()
        if len(data.data)>0:
            return True
        else:
            return False
        
    def contributor_exists(self, discord_id):
        data = self.client.table("contributors").select("*").eq("discord_id", discord_id).execute()
        if len(data.data)>0:
            return True
        else:
            return False
    
    def add_discord_metrics(self, discord_metrics):
        data = self.client.table("discord_metrics").insert(discord_metrics).execute()
        return data

    def add_github_metrics(self, github_metrics):
        data = self.client.table("github_metrics").insert(github_metrics).execute()
        return data
                    