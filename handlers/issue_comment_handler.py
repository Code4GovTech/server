from handlers.EventHandler import EventHandler
from utils.db import SupabaseInterface
from datetime import datetime
from utils.logging_file import logger

class Issue_commentHandler(EventHandler):
    async def handle_event(self, data, supabase_client):
        try:        
            #generate sample dict for ticket comment table
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
                     
        except Exception as e:
            logger.info(f"{datetime.now()}---jobs works")
            pass
        
        
