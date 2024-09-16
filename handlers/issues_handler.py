import logging
import json
from handlers.EventHandler import EventHandler
from events.ticketEventHandler import TicketEventHandler
from utils.db import PostgresORM

class IssuesHandler(EventHandler):
    async def handle_event(self, data, postgres_client):
        # Implement your logic for handling issue events here
        try:        
            module_name = data.get("action")
            print('inside handle events')
            issue = data["issue"]
            labels = issue["labels"]
            print(f'inside issue handler with issue data as {issue} and label as {labels}')
            if next((l for l in labels if l['name'] == 'C4GT Community'), None):
                handler_method = getattr(self, f'handle_issue_{module_name}', None)
                if handler_method:
                    await handler_method(data, postgres_client)
                    await self.log_user_activity(data, postgres_client)
                else:
                    logging.info(f"No handler found for module: {module_name}")
            
            return 'success'

            
        except Exception as e:
            logging.info(e)
            raise Exception
        
    async def handle_issue_created(self, data, postgres_client):
        # Implement your logic for handling issue events here
        try:        
            if data.get("issue"):
                issue = data["issue"]
                print('inside issue created with', issue)
                if postgres_client.get_issue_from_issue_id(issue["id"]):
                    await postgres_client.delete("issues", "id", issue["id"])
                await TicketEventHandler().onTicketCreate(data)
                if await postgres_client.checkIsTicket("issues","issue_id",issue["id"]):
                    await TicketEventHandler().onTicketEdit(data)
                    if data["action"] == "closed":
                        await TicketEventHandler().onTicketClose(data)
            
        except Exception as e:
            print('exception', e)
            logging.info(e)
            raise Exception
        
    async def handle_issue_opened(self, data, postgres_client):
        # Implement your logic for handling issue events here
        try:        
            if data.get("issue"):
                issue = data["issue"]
                print('inside issue opened with', issue)
                await TicketEventHandler().processDescription(data)
            
        except Exception as e:
            logging.info(e)
            raise Exception
        
    async def handle_issue_labeled(self, data, postgres_client):
        try:
            print(json.dumps(data, indent=4))
            issue = data["issue"]
            print('inside issue labeled with', issue)
            db_issue = self.postgres_client.get_data('id', 'issues', issue["id"])
            if not db_issue:
                await self.handle_issue_opened(data, postgres_client)
            labels = issue["labels"]
            print(labels)
            if labels:
                db_issue["labels"] = labels["name"]
                self.postgres_client.update_data(db_issue, 'id', 'issues')
                
            return "success"
        except Exception as e:
            logging.info(e)
            raise Exception
        
    async def handle_issue_edited(self, data, postgres_client):
        try:
            print(json.dumps(data, indent=4))
            issue = data["issue"]
            print('inside issue edited with', issue)
            db_issue = self.postgres_client.get_data('issue_id', 'issues', issue["id"], "*")
            if not db_issue:
                await self.handle_issue_opened(data, postgres_client)
            
            body = issue["body"]
            print(body)
            if body:
                await TicketEventHandler().processDescription(data)
                
            return "success"
        except Exception as e:
            print(e)
            logging.info(e)
            raise Exception


    async def handle_issue_closed(self, data, postgres_client):
        try:
            issue = data["issue"]
            print('inside issue closed with', issue)
            issue = self.postgres_client.get_data('issue_id', 'issues', issue["id"])
            if issue:
                issue["status"] = "closed"
                self.postgres_client.update_data(issue, 'id', 'issues')
            return "success"
        except Exception as e:
            logging.info(e)
            raise Exception
        

    async def log_user_activity(self, data, postgres_client):
        try:
            issue = data["issue"]
            print('inside user activity', issue)
            issue = self.postgres_client.get_data('issue_id', 'issues', issue["id"])

            user_id = data['issue']['user']['id']
            
            contributor = self.postgres_client.get_data('github_id', 'contributors_registration', user_id, '*')
            contributor_id = contributor["id"]

            activity_data = {
                "issue_id": issue["id"],
                "activity": f"issue_{data['action']}",
                "created_at": issue['created_at'],
                "updated_at": issue['updated_at'],
                "contributor_id": contributor_id,
                "mentor_id": ""
            }
            saved_activity_data = postgres_client.add_data(activity_data,"user_activity")
            return saved_activity_data
        
        except Exception as e:
            logging.info(e)
            raise Exception

