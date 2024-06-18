import logging
from handlers.EventHandler import EventHandler


class Pull_requestHandler(EventHandler):
    async def handle_event(self, data, supabase_client):
        # Implement your logic for handling issue events here
        try:            
            pr_data = {
                "created_at": data['pull_request']['created_at'],
                "api_url":None,
                "html_url": data['pull_request']['html_url'],
                "raised_by": data['pull_request']['user']['id'],
                "raised_at":  data['pull_request']['updated_at'],
                "raised_by_username": data['pull_request']['user']['login'],
                "status": data['action'],
                "is_merged": data['pull_request']['merged'],
                "merged_by": data['pull_request']['merged_by'],
                "merged_at": data['pull_request']['merged_at'],
                "merged_by_username": None,
                "pr_id": data['pull_request']['id'],
                "points": 5,
                "ticket_url": data['pull_request']['issue_url'],
                "ticket_complexity": "medium"
            }
            
            points = supabase_client.get_data("url","ccbp_tickets",data['pull_request']['issue_url'],None)  
            pr_data['points'] = points[0]['ticket_points'] if points else 0
            
            save_data = supabase_client.add_data(pr_data,"pr_history")            
            if save_data == None:
                logging.info("Failed to save data in pr_history")
            
        except Exception as e:
            logging.info(e)
            raise Exception
        
        

