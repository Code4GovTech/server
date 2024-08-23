from handlers.EventHandler import EventHandler
from utils.db import SupabaseInterface
from datetime import datetime
from utils.logging_file import logger

class Issue_commentHandler(EventHandler):
    async def handle_event(self, data, postgres_client):
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
                        
            if data['issue']['state'] == "closed":
                issue = await postgres_client.get_issue_from_issue_id(data['issue']['id'])                
                contributors = await postgres_client.get_contributors_from_issue_id(issue[0]['id']) if issue else None
                
                #FIND POINTS BY ISSUE COMPLEXITY
                points = await postgres_client.get_pointsby_complexity(issue[0]['complexity'])
                
                #SAVE POINT IN POINT_TRANSACTIONS & USER POINTS
                add_points = await postgres_client.upsert_point_transaction(issue[0]['id'],contributors[0]['contributor_id'],points)
                add_user_points= await postgres_client.save_user_points(contributors[0]['contributor_id'],points)
                            
            save_data = await postgres_client.add_data(comment_data,"ticket_comments")            
            if save_data == None:
                logger.info(f"{datetime.now()}--- Failed to save data in ticket_comments")
                     
        except Exception as e:
            logger.info(f"{datetime.now()}---{e}")
            raise Exception 
        
        
