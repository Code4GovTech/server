import os, sys
from typing import Any
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from abc import ABC, abstractmethod

client_options = ClientOptions(postgrest_client_timeout=None)
import dotenv

dotenv.load_dotenv(".env")

# url: str = os.getenv("SUPABASE_URL")
# key: str = os.getenv("SUPABASE_KEY")




class SupabaseInterface():
    
    _instance = None
    
    def __init__(self):
        # Initialize Supabase client upon first instantiation
        if not SupabaseInterface._instance:
            self.supabase_url = os.getenv("SUPABASE_URL")
            self.supabase_key = os.getenv("SUPABASE_KEY")
            self.client: Client = create_client(self.supabase_url, self.supabase_key, options=client_options)
            SupabaseInterface._instance = self
        else:          
            SupabaseInterface._instance = self._instance
        
    

    @staticmethod
    def get_instance():
        # Static method to retrieve the singleton instance
        if not SupabaseInterface._instance:
            # If no instance exists, create a new one
            SupabaseInterface._instance = SupabaseInterface()
        return SupabaseInterface._instance
    
       
    def readAll(self, table):
        data = self.client.table(f"{table}").select("*").execute()
        return data.data
    
    def read(self, table, filters=None, select='*', order=None, limit=None, offset=None):
        """
        Reads data from a table in Supabase.

        Parameters:
        - table (str): Name of the table from which to read data.
        - filters (dict, optional): Filtering conditions. Values can be simple values for exact matches 
                                    or tuples like ('gt', value) for greater than conditions.
        - select (str, optional): The specific columns you want to select. Defaults to '*'.
        - order (dict, optional): Ordering conditions, with column names as keys and ordering direction ('asc' or 'desc') as values.
        - limit (int, optional): Maximum number of records to fetch.
        - offset (int, optional): Number of records to skip.

        Returns:
        - List[dict]: List of dictionaries representing the rows from the table.
        """
        query = self.client.table(table).select(select)
        
        if filters:
            for column, condition in filters.items():
                # Check if the condition is a tuple (e.g., ('gt', 0))
                if isinstance(condition, tuple) and len(condition) == 2:
                    operation, value = condition
                    if operation == 'gt':
                        query = query.filter(column, 'gt', value)
                    # Add more conditions (e.g., 'lt', 'gte', 'lte', etc.) as needed
                else:
                    query = query.eq(column, condition)
        
        if order:
            for column, direction in order.items():
                query = query.order(column, ascending=(direction == 'asc'))

        if limit:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)
            
        data = query.execute()
        return data.data




    
    def insert(self,table, data):
        data = self.client.table(table).insert(data).execute()
        return data.data
    
    def recordComment(self, data):
        data = self.client.table("app_comments").insert(data).execute()
        return data.data
    
    def updateComment(self, data):
        data = self.client.table("app_comments").update(data).eq("issue_id", data["issue_id"]).execute()
        return data.data
    
    def update(self,table, update, query_key, query_value):
        data = self.client.table(table).update(update).eq(query_key, query_value).execute()
        return data.data
    
    def readCommentData(self, issue_id):
        data = self.client.table("app_comments").select("*").eq("issue_id", issue_id).execute()
        return data.data
    
    def insert(self, table, data):
        data = self.client.table(table).insert(data).execute()
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
        ccbpResp = self.client.table("ccbp_tickets").select("*").eq("issue_id", issue_id).execute()
        dmpResp = self.client.table("dmp_tickets").select("*").eq("issue_id", issue_id).execute()
        data = ccbpResp.data + dmpResp.data
        # unlisted_data = self.client.table("unlisted_tickets").select("*").eq("issue_id", issue_id).execute()
        if len(data)>0:
            return True
        else:
            return False
    
    def checkIsDMPTicket(self, issue_id):
        data = self.client.table("dmp_tickets").select("*").eq("issue_id", issue_id).execute()
        # unlisted_data = self.client.table("unlisted_tickets").select("*").eq("issue_id", issue_id).execute()
        if len(data.data)>0:
            return True
        else:
            return False
    
    def checkUnlisted(self, issue_id):
        unlisted_data = self.client.table("unlisted_tickets").select("*").eq("issue_id", issue_id).execute()
        if len(unlisted_data.data)>0:
            return True
        else:
            return False
    
    def deleteUnlistedTicket(self, issue_id):
        data = self.client.table("unlisted_tickets").delete().eq("issue_id", issue_id).execute()
        return data.data

    
    def getTicket(self, issue_id):
        data = self.client.table("ccbp_tickets").select("*").eq("issue_id", issue_id).execute()
        if len(data.data)==0:
            data = self.client.table("dmp_tickets").select("*").eq("issue_id", issue_id).execute()
        return data.data
    
    def deleteTicket(self, issue_id):
        data = self.client.table("ccbp_tickets").delete().eq("issue_id", issue_id).execute()
        data = self.client.table("dmp_tickets").delete().eq("issue_id", issue_id).execute()
        return data.data
    
    def update_recorded_ticket(self, data):
        data = self.client.table("ccbp_tickets").update(data).eq("issue_id", data["issue_id"]).execute()
        return data.data
    
    def updateRecordedDMPTicket(self, data):
        data = self.client.table("dmp_tickets").update(data).eq("issue_id", data["issue_id"]).execute()
        return data.data
        

    
    def isPrRecorded(self, id):
        data = self.client.table("pull_requests").select("*").eq("pr_id", id).execute()
        if len(data.data)>0:
            return True
        else:
            return False
    
    def addPr(self, prData, issue_id):
        if issue_id:
            ticket = self.getTicket(issue_id)
            # print(ticket, type(ticket), file=sys.stderr)
        for pr in prData:
            data = {
                        # "api_url":data["url"],
                        "html_url":pr["html_url"],
                        "pr_id":pr["pr_id"],
                        "raised_by":pr["raised_by"],
                        "raised_at":pr["raised_at"],
                        "raised_by_username":pr["raised_by_username"],
                        "status":pr["status"],
                        "is_merged":pr["is_merged"] if pr.get("is_merged") else None,
                        "merged_by":pr["merged_by"] if pr["merged_by"] else None,
                        "merged_by_username":pr["merged_by_username"] if pr.get("merged_by_username") else None,
                        "merged_at":pr["merged_at"] if pr.get("merged_at") else None,
                        "points": ticket[0]["ticket_points"] if issue_id else 0,
                        "ticket_url":ticket[0]["api_endpoint_url"]
                    }
            resp = self.client.table("connected_prs").insert(data).execute()
        return

    def add_mentor(self, userdata):
        
        data = self.client.table("mentors").insert(userdata).execute()
        # print(data.data)
        return data
    
    def update_contributor(self, discord_id, user_data):
        data = self.client.table("contributors_registration").update(user_data).eq("discord_id", discord_id).execute()
        return data

    
    def add_contributor(self, userdata):
        data = self.client.table("contributors_registration").insert(userdata).execute()
        # print(data.data)
        return data
    
    def mentor_exists(self, discord_id):
        data = self.client.table("mentors").select("*").eq("discord_id", discord_id).execute()
        if len(data.data)>0:
            return True
        else:
            return False
    
    def register_contributor(self, discord_id, user_data):
        try:
            self.client.table("contributors_registration").insert(user_data).execute()
        except Exception as e:
            print(e)

        
        # existing_data = contributors_table.select("*").eq("discord_id", discord_id).execute()
        
        # if len(existing_data.data) > 0:
        #     contributors_table.update(user_data).eq("discord_id", discord_id).execute()
        # else:
        #     contributors_table.insert(user_data).execute()
        
    def contributor_exists(self, discord_id):
        data = self.client.table("contributors_registration").select("*").eq("discord_id", discord_id).execute()
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
            # print(issues, file=sys.stderr)
            return issues.data
        data = self.client.table("ccbp_tickets").insert(data).execute()
        # print(data, file=sys.stderr)
        return data.data
    
    def recordCreatedDMPTicket(self, data):
        issues = self.client.table("dmp_tickets").select("*").eq("issue_id",data["issue_id"]).execute()
        if len(issues.data)>0:
            # print(issues, file=sys.stderr)
            return issues.data
        data = self.client.table("dmp_tickets").insert(data).execute()
        # print(data, file=sys.stderr)
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
    
    #Generic function for CRUD                    
    def delete_record(self, table, column, value):
        data = self.client.table(table).delete().eq(column, value).execute()
        return data.data
    
    def add_data(self, data,table_name):
        data = self.client.table(table_name).insert(data).execute()
        return data.data
    
    
    def update_data(self, data,col_name,table_name):
        data = self.client.table(table_name).update(data).eq(col_name, data[col_name]).execute()

        return data.data

    def get_data(self, col_name,table_name,value,condition):
        if condition == None:
            condition = "*"
        data = self.client.table(table_name).select(condition).eq(col_name, value).execute()
       
        return data.data
    
    def check_record_exists(self,table_name,col_name,col_value,condition):
        unlisted_data = self.client.table(table_name).select(condition).eq(col_name, col_value).execute()
        if len(unlisted_data.data)>0:
            return True
        else:
            return False
            
    def multiple_update(self, table, update_data, filters):
        query = self.client.table(table).update(update_data)
        if filters:
            for column, condition in filters.items():
                if isinstance(condition, tuple) and len(condition) == 2:
                    operation, value = condition
                    query = query.filter(column, operation, value)
                else:
                    query = query.eq(column, condition)
        data = query.execute()
        return data.data
    
    def multiple_delete(self, table, filters):
        query = self.client.table(table).delete()
        if filters:
            for column, condition in filters.items():
                if isinstance(condition, tuple) and len(condition) == 2:
                    operation, value = condition
                    query = query.filter(column, operation, value)
                else:
                    query = query.eq(column, condition)
        data = query.execute()
        return data.data
    
    
    