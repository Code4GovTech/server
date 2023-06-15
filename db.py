import os
from typing import Any
from supabase import create_client, Client
import dotenv

dotenv.load_dotenv(".env")

# url: str = os.getenv("SUPABASE_URL")
# key: str = os.getenv("SUPABASE_KEY")

class SupabaseInterface:
    def __init__(self) -> None:
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
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

        for metric in discord_metrics:
            data = self.client.table("discord_metrics").select("*").eq("product_name", metric["product_name"]).execute()
            if len(data.data)>0:
                data = self.client.table("discord_metrics").update({"mentor_messages": metric["mentor_messages"], "contributor_messages": metric["contributor_messages"]}).eq("product_name", metric["product_name"]).execute()
            else:
                data = self.client.table("discord_metrics").insert(metric).execute()
        return data
    
    def record_created_ticket(self, data):
        data = self.client.table("ccbp_tickets").insert(data).execute()
        print(data)
        return data.data
    
    def add_engagement(self, github_id):
        contributor = self.client.table("contributor_engagement").select("*").eq("contributor_github",github_id).execute()
        comment_count = contributor.data[0]["github_comments"]
        data = self.client.table("contributor_engagement").update({"github_comments":comment_count+1}).eq("contributor_github",github_id).execute()
        return data

    
    def add_event_data(self, data):
        data_ = {
            "event_data": data
        }
        data = self.client.table("github_events_data_dump").insert(data_).execute()
        return data

    def add_github_metrics(self, github_metrics):
        for metric in github_metrics:
            data = data = self.client.table("github_metrics").select("*").eq("product_name", metric["product_name"]).execute()
            if len(data.data)>0:
                #this is updatating product name which is bad
                data = self.client.table("github_metrics").update(metric).eq("product_name", metric["product_name"]).execute()
            else:
                data = self.client.table("github_metrics").insert(metric).execute()
        return data
                    