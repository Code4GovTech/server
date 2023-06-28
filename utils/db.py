import os, sys
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
    
    def recordComment(self, data):
        data = self.client.table("app_comments").insert(data).execute()
        return data.data
    
    def updateComment(self, data):
        data = self.client.table("app_comments").update(data).eq("issue_id", data["issue_id"]).execute()
        return data.data
    
    def readCommentData(self, issue_id):
        data = self.client.table("app_comments").select("*").eq("issue_id", issue_id).execute()
        return data.data

    
    def commentExists(self,issue_id):
        data = self.client.table("app_comments").select("*").eq("issue_id", issue_id).execute()
        if len(data.data)>0:
            return True
        else:
            return False
    def deleteComment(self, issue_id):
        data = self.client.table("app_comments").delete().eq("issue_id", issue_id).execute()
        return data.data

    def dump_dev_data(self, data):
        data = self.client.table("dev_data").insert(data).execute()
        return
    
    def checkIsTicket(self, issue_id):
        data = self.client.table("ccbp_tickets").select("*").eq("issue_id", issue_id).execute()
        if len(data.data)>0:
            return True
        else:
            return False
    
    def getTicket(self, issue_id):
        data = self.client.table("ccbp_tickets").select("*").eq("issue_id", issue_id).execute()
        return data.data
    
    def deleteTicket(self, issue_id):
        data = self.client.table("ccbp_tickets").delete().eq("issue_id", issue_id).execute()
        return data.data
    
    def update_recorded_ticket(self, data):
        data = self.client.table("ccbp_tickets").update(data).eq("issue_id", data["issue_id"]).execute()
        return data.data
        

    
    def isPrRecorded(self, id):
        data = self.client.table("pull_requests").select("*").eq("pr_id", id).execute()
        if len(data.data)>0:
            return True
        else:
            return False
    
    def addPr(self, data, issue_id):
        ticket = self.getTicket(issue_id)
        data = {
                    "api_url":data["url"],
                    "html_url":data["html_url"],
                    "pr_id":data["id"],
                    "raised_by":data["user"]["id"],
                    "raised_at":data["created_at"],
                    "raised_by_username":data["user"]["login"],
                    "status":data["state"],
                    "is_merged":data["merged"],
                    "merged_by":data["merged_by"]["id"] if data["merged"] else None,
                    "merged_by_username":data["merged_by"]["login"] if data["merged"] else None,
                    "merged_at":data["merged_at"] if data["merged"] else None,
                    "points": ticket["ticket_points"]
                }
        data = self.client.table("pull_requests").insert(data).execute()
        return data.data

    def add_mentor(self, userdata):
        
        data = self.client.table("mentors").insert(userdata).execute()
        # print(data.data)
        return data
    
    def update_contributor(self, discord_id, user_data):
        data = self.client.table("contributors").update(user_data).eq("discord_id", discord_id).execute()
        return data

    
    def add_contributor(self, userdata):
        
        data = self.client.table("contributors").insert(userdata).execute()
        # print(data.data)
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
        issues = self.client.table("ccbp_tickets").select("*").eq("issue_id",data["issue_id"]).execute()
        if len(issues.data)>0:
            print(issues, file=sys.stderr)
            return issues.data
        data = self.client.table("ccbp_tickets").insert(data).execute()
        print(data, file=sys.stderr)
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
                    