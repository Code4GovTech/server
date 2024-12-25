from handlers.EventHandler import EventHandler
from datetime import datetime
from utils.logging_file import logger
import logging
from utils.user_activity import UserActivity
from shared_migrations.db.server import ServerQueries

class Issue_commentHandler(EventHandler):
    def __init__(self):
        self.postgres_client = ServerQueries()
     
    async def handle_event(self, data, postgres_client):
        try:        
            module_name = data.get("action")
            print('inside handle events')
            issue = data["issue"]
            print('inside issue comment handler ', issue)
            labels = issue["labels"]
            if next((l for l in labels if l['name'].lower() == 'c4gt community'), None):
                handler_method = getattr(self, f'handle_issue_comment_{module_name}', None)
                if handler_method:
                    await handler_method(data)
                    await UserActivity.log_user_activity(data, 'comment')
                else:
                    logging.info(f"No handler found for module: {module_name}")
            
            return 'success'

            
        except Exception as e:
            logging.info(e)
            raise Exception
        
    async def handle_issue_comment_created(self, data):
        try:        
            #generate sample dict for ticket comment table
            print(f'creating comment with {data["issue"]}')
            comment_data = {
                'url':data['issue']['comments_url'],
                'html_url':data['issue']['html_url'],
                'issue_url':data['comment']['issue_url'],
                'issue_id': data['issue']['id'],
                'comment_id': data['comment']['id'],
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

            print('comments data ', comment_data)
                        
            save_data = await self.postgres_client.add_data(comment_data,"ticket_comments") 
            print('saved data in comments created ', save_data)           
            if save_data == None:
                logger.info(f"{datetime.now()}--- Failed to save data in ticket_comments")
                     
        except Exception as e:
            logger.info(f"{datetime.now()}---{e}")
            raise Exception 
        
    
    async def handle_issue_comment_edited(self, data):
        try:        
            #generate sample dict for ticket comment table
            print(f'editing comment with {data["issue"]}')
            comment_data = {
                'content':data['comment']['body'],
                'id':data['comment']['id'],
                'updated_at':str(datetime.now())
            }
            
            save_data = await self.postgres_client.update_data(comment_data, "id", "ticket_comments")   
            print('saved data in comments edited ', save_data)          
            if save_data == None:
                logger.info(f"{datetime.now()}--- Failed to save data in ticket_comments")
                     
        except Exception as e:
            logger.info(f"{datetime.now()}---{e}")
            raise Exception 
        
    async def handle_issue_comment_deleted(self, data):
        try:
            print(f'deleting comment with {data["issue"]}')
            comment_id = data['comment']['id']
            # data = await postgres_client.deleteIssueComment(comment_id)
            await self.postgres_client.delete("ticket_comments","id", comment_id)
            print('data in comment deleted', data) 
        except Exception as e:
            print('Exception occured ', e)
            logger.info(f"{datetime.now()}---{e}")
            raise Exception

        
        
