import logging
from handlers.EventHandler import EventHandler
from datetime import datetime

class Pull_requestHandler(EventHandler):

    def convert_to_datetime(self, date_str):
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')

    async def handle_event(self, data, postgres_client):
        # Implement your logic for handling issue events here
        try:
            print('inside pull request handler ', data) 
            merged_by =  data['pull_request']['merged_by']['id'] if data['pull_request']['merged_by'] else None
            merged_at = data['pull_request']['merged_at']
            merged_by_username =  data['pull_request']['merged_by']['login'] if data['pull_request']['merged_by'] else None 
            created_at =  self.convert_to_datetime(data['pull_request']['created_at']) 
            raised_at = self.convert_to_datetime(data['pull_request']['updated_at'])
            if merged_at:
                merged_at = self.convert_to_datetime(merged_at)
            pr_data = {
                "created_at": created_at,
                "api_url":data['pull_request']['url'],
                "html_url": data['pull_request']['html_url'],
                "raised_by": data['pull_request']['user']['id'],
                "raised_at":  raised_at,
                "raised_by_username": data['pull_request']['user']['login'],
                "status": data['action'],
                "is_merged": data['pull_request']['merged'],
                "merged_by": merged_by,
                "merged_at": str(merged_at),
                "merged_by_username":  merged_by_username,
                "pr_id": data['pull_request']['id'],
                "points": 0,
                "ticket_url": data['pull_request']['issue_url'],
                "ticket_complexity": None
            }

            print('PR data ', pr_data)
            
            pr_exist = await postgres_client.get_data('pr_id', 'pr_history',  data['pull_request']['id'])
            if pr_exist:
                save_data = await postgres_client.update_pr_history(pr_data["pr_id"],pr_data)
            else:
                save_data = await postgres_client.add_data(pr_data,"pr_history")
            print('saved data in PR ', save_data)            
            if save_data == None:
                logging.info("Failed to save data in pr_history")

            user_id = data['pull_request']['user']['id']

            #get contributor_id and save to supabase
            contributor = await postgres_client.get_data('github_id', 'contributors_registration', user_id)
            if not contributor:
                print('could not add contributors data contributor does not exist')
                return pr_data
            contributor_id = contributor["id"]

            issue_url = data['pull_request']['issue_url']
            issue = await postgres_client.get_data('issue_url', 'issues', issue_url, '*')

            #save activity to user_activity
            activity_data = {
                "issue_id": issue["id"],
                "activity": f"pull_request_{data['action']}",
                "created_at": data['pull_request']['created_at'],
                "updated_at": data['pull_request']['updated_at'],
                "contributor_id": contributor_id,
                "mentor_id": ""
            }
            saved_activity_data = await postgres_client.add_data(activity_data,"user_activity")
        except Exception as e:
            print('exception in pr ', e)
            logging.info(e)
            raise Exception
        
        

