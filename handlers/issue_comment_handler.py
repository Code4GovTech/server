from handlers.EventHandler import EventHandler
from datetime import datetime
from utils.logging_file import logger
import logging

class Issue_commentHandler(EventHandler):
     
    async def handle_event(self, data, postgres_client):
        try:        
            module_name = data.get("action")
            print('inside handle events')
            issue = data["issue"]
            print('inside issue comment handler ', issue)
            labels = issue["labels"]
            if next((l for l in labels if l['name'] == 'C4GT Community'), None):
                handler_method = getattr(self, f'handle_issue_comment{module_name}', None)
                if handler_method:
                    await handler_method(data, postgres_client)
                else:
                    logging.info(f"No handler found for module: {module_name}")
            
            return 'success'

            
        except Exception as e:
            logging.info(e)
            raise Exception
        
    async def handle_issue_comment_created(self, data, postgres_client):
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
                        
            if data['issue']['state'] == "closed":
                issue = await postgres_client.get_issue_from_issue_id(data['issue']['id'])                
                contributors = await postgres_client.get_contributors_from_issue_id(issue[0]['id']) if issue else None
                
                #FIND POINTS BY ISSUE COMPLEXITY
                points = await postgres_client.get_pointsby_complexity(issue[0]['complexity'])
                
                #SAVE POINT IN POINT_TRANSACTIONS & USER POINTS
                add_points = await postgres_client.upsert_point_transaction(issue[0]['id'],contributors[0]['contributor_id'],points)
                add_user_points= await postgres_client.save_user_points(contributors[0]['contributor_id'],points)
                            
            save_data = await postgres_client.add_data(comment_data,"ticket_comments") 
            print('saved data in comments created ', save_data)           
            if save_data == None:
                logger.info(f"{datetime.now()}--- Failed to save data in ticket_comments")
                     
        except Exception as e:
            logger.info(f"{datetime.now()}---{e}")
            raise Exception 
        
    
    async def handle_issue_comment_edited(self, data, postgres_client):
        try:        
            #generate sample dict for ticket comment table
            print(f'editing comment with {data['issue']}')
            comment_data = {
                'content':data['comment']['body'],
                'id':data['comment']['id'],
                'updated_at':str(datetime.now())
            }
            
            save_data = postgres_client.update_data(comment_data, "id", "ticket_comments")   
            print('saved data in comments edited ', save_data)          
            if save_data == None:
                logger.info(f"{datetime.now()}--- Failed to save data in ticket_comments")
                     
        except Exception as e:
            logger.info(f"{datetime.now()}---{e}")
            raise Exception 
        
    async def handle_issue_comment_deleted(self, data, postgres_client):
        try:
            print(f'deleting comment with {data['issue']}')
            comment_id = data['comment']['id']
            data = postgres_client.deleteIssueComment(comment_id)
            print('data in comment deleted', data) 
        except Exception as e:
            logger.info(f"{datetime.now()}---{e}")
            raise Exception

        
        
