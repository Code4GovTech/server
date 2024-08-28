import logging
from handlers.EventHandler import EventHandler


class Pull_requestHandler(EventHandler):
    async def handle_event(self, data, postgres_client):
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
                "merged_by": data['pull_request']['merged_by']['id'],
                "merged_at": data['pull_request']['merged_at'],
                "merged_by_username":  data['pull_request']['merged_by']['login'],
                "pr_id": data['pull_request']['id'],
                "points": 0,
                "ticket_url": data['pull_request']['issue_url'],
                "ticket_complexity": None
            }
            
            points = await postgres_client.get_data("url","ccbp_tickets",data['pull_request']['issue_url'],None)  
            pr_data['points'] = points[0]['ticket_points'] if points else 0
            pr_data['ticket_complexity'] = points[0]['complexity'] if points else None
            
            save_data = await postgres_client.add_data(pr_data,"pr_history")            
            if save_data == None:
                logging.info("Failed to save data in pr_history")

            user_id = data['pull_request']['user']['id']

            #get contributor_id and save to supabase
            contributor = supabase_client.get_data('github_id', 'contributors_registration', user_id, '*')
            contributor_id = contributor["id"]

            issue_url = data['pull_request']['issue_url']
            issue = supabase_client.get_data('issue_url', 'issues', issue_url, '*')

            #save activity to user_activity
            activity_data = {
                "issue_id": issue["id"],
                "activity": f"pull_request_{data['action']}",
                "created_at": data['pull_request']['created_at'],
                "updated_at": data['pull_request']['updated_at'],
                "contributor_id": contributor_id,
                "mentor_id": ""
            }
            saved_activity_data = supabase_client.add_data(activity_data,"user_activity")
        except Exception as e:
            logging.info(e)
            raise Exception
        
        

