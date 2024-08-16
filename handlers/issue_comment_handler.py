from handlers.EventHandler import EventHandler
from utils.db import SupabaseInterface
from datetime import datetime
from utils.logging_file import logger
import logging

class Issue_commentHandler(EventHandler):
    def __init__(self):
        self.supabase_client = SupabaseInterface.get_instance()
        return
     
    async def handle_event(self, data, supabase_client):
        try:        
            module_name = data.get("action")
            print('inside handle events')
            issue = data["issue"]
            labels = issue["labels"]
            if next((l for l in labels if l['name'] == 'C4GT Community'), None):
                handler_method = getattr(self, f'handle_issue_comment{module_name}', None)
                if handler_method:
                    await handler_method(data, supabase_client)
                else:
                    logging.info(f"No handler found for module: {module_name}")
            
            return 'success'

            
        except Exception as e:
            logging.info(e)
            raise Exception
        
    async def handle_issue_comment_created(self, data, supabase_client):
        try:        
            #generate sample dict for ticket comment table
            print(f'creating comment with {data['issue']}')
            comment_data = {
                'url':data['issue']['comments_url'],
                'html_url':data['issue']['html_url'],
                'issue_url':data['comment']['issue_url'],
                'node_id':data['issue']['node_id'],
                'commented_by':data['comment']['user']['login'],
                'commented_by_id':data['comment']['user']['id'],
                'content':data['comment']['body'],
                'reactions_url':data['comment']['reactions']['url'],
                'ticket_url':data['issue']['url'],
                'id':data['comment']['id'],
                'created_at':str(datetime.now()),
                'updated_at':str(datetime.now())
                
            }
            
            save_data = supabase_client.add_data(comment_data,"ticket_comments")            
            if save_data == None:
                logger.info(f"{datetime.now()}--- Failed to save data in ticket_comments")
                     
        except Exception as e:
            logger.info(f"{datetime.now()}---{e}")
            raise Exception 
        
    
    async def handle_issue_comment_edited(self, data, supabase_client):
        try:        
            #generate sample dict for ticket comment table
            print(f'editing comment with {data['issue']}')
            comment_data = {
                'content':data['comment']['body'],
                'id':data['comment']['id'],
                'updated_at':str(datetime.now())
            }
            
            save_data = supabase_client.update_data(comment_data, "id", "ticket_comments")            
            if save_data == None:
                logger.info(f"{datetime.now()}--- Failed to save data in ticket_comments")
                     
        except Exception as e:
            logger.info(f"{datetime.now()}---{e}")
            raise Exception 
        
    async def handle_issue_comment_deleted(self, data, supabase_client):
        try:
            print(f'deleting comment with {data['issue']}')
            comment_id = data['comment']['id']
            data = supabase_client.deleteIssueComment(comment_id)
        except Exception as e:
            logger.info(f"{datetime.now()}---{e}")
            raise Exception

        
        
